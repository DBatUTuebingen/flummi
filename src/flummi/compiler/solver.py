from dataclasses import dataclass

from flummi.compiler.analyzer import AnalysisResult

from ..IR.CFP import (
    Program,
    Primitive,
    Start,
    Assignment,
    Emit,
    Where,
    GoTo,
    Variable,
    Label,
    Expression,
)

from ..library import utils, graph
from .names import SystemVariable

__all__ = ("solve",)


type PerLabel[T] = dict[Label, T]


@dataclass(frozen=True, slots=True)
class DataflowResult:
    inputs_of: PerLabel[set[Variable]]
    outputs_of: PerLabel[set[Variable]]


def solve(program: Program, analysis: AnalysisResult) -> DataflowResult:
    return Solver(program, analysis).run()


@dataclass
class Solver:
    _program: Program
    _analysis: AnalysisResult

    def run(self) -> DataflowResult:
        cfp = self._program.body
        inputs = {
            label: self.uses(primitive)
            for label, primitive in cfp.primitives.items()
        }
        outputs = {
            label: self.binds(primitive)
            for label, primitive in cfp.primitives.items()
        }

        all_successors_of = graph.merge(
            cfp.successors_of,
            cfp.virtual_successors_of,
        )

        changed = True
        while changed:
            changed = False
            for label in cfp.primitives:
                new_outputs = utils.union(
                    inputs[successor] for successor in all_successors_of[label]
                )

                new_outputs -= outputs[label]

                if not new_outputs:
                    continue

                changed = True
                inputs[label] |= new_outputs
                outputs[label] |= new_outputs

        return DataflowResult(inputs, outputs)

    def uses(self, primitive: Primitive) -> set[Variable]:
        match primitive:
            case Start():
                return {self._analysis.system_variables[SystemVariable.LABEL]}

            case Assignment(_, Expression(_, variables)):
                return {
                    *variables,
                    self._analysis.system_variables[SystemVariable.CONTROL],
                }

            case Emit(variable):
                return {variable}

            case Where(variable, _):
                return {variable}

            case _:
                return {self._analysis.system_variables[SystemVariable.CONTROL]}

    def binds(self, primitive: Primitive) -> set[Variable]:
        match primitive:
            case Start():
                return {self._analysis.system_variables[SystemVariable.CONTROL]}

            case Assignment(variable, _):
                return {variable}

            case Emit(_):
                return {self._analysis.system_variables[SystemVariable.RESULT]}

            case GoTo():
                return {self._analysis.system_variables[SystemVariable.LABEL]}

            case _:
                return set()
