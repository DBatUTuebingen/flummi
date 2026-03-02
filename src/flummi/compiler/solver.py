from dataclasses import dataclass

from ..IR import CFP, common
from ..library import utils, errors
from . import names

__all__ = ("solve",)


@dataclass
class Dataflow:
    inputs: dict[CFP.Label, set[common.Identifier]]
    outputs: dict[CFP.Label, set[common.Identifier]]


def solve(program: CFP.Program) -> Dataflow:
    return DataflowSolver().solve_program(program)


@dataclass
class DataflowSolver:
    def solve_program(self, program: CFP.Program) -> Dataflow:
        cfp = program.body

        inputs, outputs = self.live_variable_analysis(cfp)

        return Dataflow(inputs, outputs)

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
            case CFP.Assignment(_, common.Expression(_, variables)):
                return {*variables, CONTROL(primitive.location)}

            case CFP.Emit(variable):
                return {variable}

            case CFP.Where(variable, _):
                return {variable}

            case _:
                return {CONTROL(primitive.location)}

    @staticmethod
    def binds(primitive: CFP.Primitive) -> set[common.Identifier]:
        match primitive:
            case CFP.Start():
                return {CONTROL(primitive.location)}

            case CFP.Assignment(variable, _):
                return {variable}

            case CFP.Emit(_):
                return {RESULT(primitive.location)}

            case _:
                return set()


def RESULT(location: errors.Location) -> common.Identifier:
    return common.Identifier(names.result, location=location)


def CONTROL(location: errors.Location) -> common.Identifier:
    return common.Identifier(names.control, location=location)
