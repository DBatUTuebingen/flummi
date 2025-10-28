from ...IR import CFP, common
from ...library import utils, graph
from .. import constants

__all__ = ("analyze_live_variables",)


type Variables = set[CFP.Variable]

type InputMap = CFP.PerLabel[Variables]
type OutputMap = CFP.PerLabel[Variables]


def analyze_live_variables(
    program: CFP.Program,
    system_variables: dict[constants.Names, CFP.Variable],
) -> tuple[InputMap, OutputMap]:
    def uses(primitive: CFP.Primitive) -> Variables:
        match primitive:
            case CFP.Start():
                return {system_variables[constants.Names.LABEL]}

            case CFP.Let(_, common.Expression(_, variables)) | CFP.Fork(
                _, common.Expression(_, variables)
            ):
                return set(variables)

            case CFP.Where(variable) | CFP.WhereNot(variable):
                return {variable}

            case CFP.Emit(variable):
                return {
                    variable,
                    system_variables[constants.Names.ITERATION],
                }

            case CFP.GoTo(_):
                return {system_variables[constants.Names.ITERATION]}

            case CFP.Gather(aggregates, keys):
                return utils.union(
                    set(expression.arguments)
                    for expression in aggregates.values()
                ) | set(keys)

            case _:
                return set()

    def binds(primitive: CFP.Primitive) -> Variables:
        match primitive:
            case CFP.Let(variable, _) | CFP.SiblingProbe(variable, _):
                return {variable}

            case CFP.Emit(_):
                assert constants.Names.RESULT in system_variables
                return {
                    system_variables[constants.Names.RESULT],
                    system_variables[constants.Names.ITERATION],
                }

            case CFP.GoTo(_):
                assert constants.Names.LABEL in system_variables
                return {
                    system_variables[constants.Names.LABEL],
                    system_variables[constants.Names.ITERATION],
                }

            case CFP.Fork(variables, _):
                return set(variables)

            case CFP.Gather(aggregates, keys):
                return {*aggregates.keys(), *keys}

            case _:
                return set()

    cfp = program.body

    inputs_of: InputMap = {
        label: uses(primitive) for label, primitive in cfp.primitives.items()
    }
    outputs_of: OutputMap = {
        label: binds(primitive) for label, primitive in cfp.primitives.items()
    }

    successors_of = graph.merge(cfp.direct_edges, cfp.indirect_edges)
    predecessors_of = graph.invert(successors_of)

    worklist = set(cfp.primitives)

    while worklist:
        label = worklist.pop()

        new_outputs = (
            utils.union(
                inputs_of[successor] for successor in successors_of[label]
            )
            - outputs_of[label]
        )

        if not new_outputs:
            continue

        inputs_of[label] |= new_outputs
        outputs_of[label] |= new_outputs

        worklist |= predecessors_of[label]

    return inputs_of, outputs_of
