from ...IR import CFP, common
from ...library import utils, graph
from .. import constants

__all__ = ("analyze_live_variables",)


type VariablesPer[T] = dict[T, set[CFP.Variable]]

type InputMap = VariablesPer[CFP.Label]
type OutputMap = VariablesPer[CFP.Label]


def analyze_live_variables(
    program: CFP.Program,
    system_variables: dict[constants.Names, CFP.Variable],
) -> tuple[InputMap, OutputMap]:
    def uses(primitive: CFP.Primitive) -> set[CFP.Variable]:
        match primitive:
            case CFP.Start():
                return {system_variables[constants.Names.LABEL]}

            case CFP.Let(_, common.Expression(_, variables)):
                return set(variables)

            case (
                CFP.Emit(variable)
                | CFP.Where(variable)
                | CFP.WhereNot(variable)
            ):
                return {variable}

            case _:
                return set()

    def binds(primitive: CFP.Primitive) -> set[CFP.Variable]:
        match primitive:
            case CFP.Let(variable, _):
                return {variable}

            case CFP.Emit(_):
                assert constants.Names.RESULT in system_variables
                return {system_variables[constants.Names.RESULT]}

            case CFP.GoTo(_):
                assert constants.Names.LABEL in system_variables
                return {system_variables[constants.Names.LABEL]}

            case _:
                return set()

    cfp = program.body

    inputs_of: InputMap = {
        label: uses(primitive) for label, primitive in cfp.primitives.items()
    }
    outputs_of: OutputMap = {
        label: binds(primitive) for label, primitive in cfp.primitives.items()
    }

    successors_of = graph.merge(cfp.edges, cfp.backedges)
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
