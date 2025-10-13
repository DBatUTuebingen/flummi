from dataclasses import dataclass

from ..IR import CFP, common
from ..library import utils, graph
from . import names

__all__ = ("solve",)


@dataclass
class Dataflow:
    inputs: dict[CFP.Label, set[common.Identifier]]
    outputs: dict[CFP.Label, set[common.Identifier]]

    binding_sites: dict[CFP.Label, dict[common.Identifier, CFP.Label]]


def solve(program: CFP.Program) -> Dataflow:
    return DataflowSolver().solve_program(program)


@dataclass
class DataflowSolver:
    def solve_program(self, program: CFP.Program) -> Dataflow:
        cfp = program.body

        inputs, outputs = self.live_variable_analysis(cfp)

        binding_sites = self.collect_binding_sites(cfp)

        return Dataflow(inputs, outputs, binding_sites)

    @staticmethod
    def live_variable_analysis(
        cfp: CFP.Graph,
    ) -> tuple[
        dict[CFP.Label, set[common.Identifier]],
        dict[CFP.Label, set[common.Identifier]],
    ]:
        inputs = {
            label: DataflowSolver.uses(primitive)
            for label, primitive in cfp.primitives.items()
        }
        outputs = {
            label: DataflowSolver.binds(primitive)
            for label, primitive in cfp.primitives.items()
        }

        changed = True
        while changed:
            changed = False
            for label in cfp.primitives:
                new_outputs = utils.union(
                    inputs[successor] for successor in cfp.transitions[label]
                )

                new_outputs -= outputs[label]

                if not new_outputs:
                    continue

                changed = True
                inputs[label] |= new_outputs
                outputs[label] |= new_outputs

        return inputs, outputs

    @staticmethod
    def uses(primitive: CFP.Primitive) -> set[common.Identifier]:
        match primitive:
            case CFP.Let(_, common.Expression(_, variables)):
                return set(variables)

            case CFP.Emit(variable):
                return {variable}

            case _:
                return set()

    @staticmethod
    def binds(primitive: CFP.Primitive) -> set[common.Identifier]:
        match primitive:
            case CFP.Start():
                return {
                    common.Identifier(
                        names.nothing, location=primitive.location
                    )
                }

            case CFP.Let(variable, _):
                return {variable}

            case CFP.Emit(_):
                return {
                    common.Identifier(names.result, location=primitive.location)
                }

            case _:
                return set()

    @staticmethod
    def collect_binding_sites(
        cfp: CFP.Graph,
    ) -> dict[CFP.Label, dict[common.Identifier, CFP.Label]]:
        binding_sites: dict[CFP.Label, dict[common.Identifier, CFP.Label]] = {}
        last_binding_sites: dict[common.Identifier, CFP.Label] = {}

        for label in graph.topological_order(cfp.transitions):
            primitive = cfp.primitives[label]

            binding_sites[label] = {
                variable: last_binding_sites[variable]
                for variable in DataflowSolver.uses(primitive)
            }

            last_binding_sites.update(
                {
                    variable: label
                    for variable in DataflowSolver.binds(primitive)
                }
            )

        return binding_sites
