from dataclasses import dataclass

from ..IR.CFP import (
    Assignment,
    Emit,
    Expression,
    Fork,
    Gather,
    GoTo,
    IsSynced,
    Label,
    Primitive,
    Program,
    Start,
    Variable,
    Where,
)
from ..library import graph, utils
from .analysis import AnalysisResult
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
        inputs_of = {
            label: self.uses(primitive)
            for label, primitive in cfp.primitives.items()
        }
        outputs_of = {
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
                    inputs_of[successor]
                    for successor in all_successors_of[label]
                )

                new_outputs -= outputs_of[label]

                if not new_outputs:
                    continue

                changed = True
                inputs_of[label] |= new_outputs
                outputs_of[label] |= new_outputs

        return DataflowResult(inputs_of, outputs_of)

    def uses(self, primitive: Primitive) -> set[Variable]:
        match primitive:
            case Start():
                return {
                    self._analysis.system_variables[SystemVariable.LABEL],
                    self._analysis.system_variables[SystemVariable.ITERATION],
                }

            case Assignment(
                _,
                Expression(_, arguments),
            ) | Fork(
                _,
                Expression(_, arguments),
            ):
                return {
                    self._analysis.system_variables[SystemVariable.CONTROL],
                    *arguments,
                }

            case Emit(variable):
                return {
                    self._analysis.system_variables[SystemVariable.ITERATION],
                    variable,
                }

            case Where(variable, _):
                return {variable}

            case Gather(aggregates, keys):
                return {
                    # ? [info] basically a virtual key!
                    self._analysis.system_variables[SystemVariable.CONTROL],
                    *keys,
                    *utils.union(
                        expression.arguments
                        for expression in aggregates.values()
                    ),
                }

            case IsSynced(_, _, keys):
                return {*keys}

            case GoTo(_):
                return {
                    self._analysis.system_variables[SystemVariable.ITERATION],
                }

            case _:
                return {self._analysis.system_variables[SystemVariable.CONTROL]}

    def binds(self, primitive: Primitive) -> set[Variable]:
        match primitive:
            case Start():
                return {
                    self._analysis.system_variables[SystemVariable.CONTROL],
                    self._analysis.system_variables[SystemVariable.ITERATION],
                }

            case Assignment(variable, _) | IsSynced(variable, _, _):
                return {variable}

            case Emit(_):
                return {
                    self._analysis.system_variables[SystemVariable.RESULT],
                    self._analysis.system_variables[SystemVariable.ITERATION],
                }

            case GoTo():
                return {
                    self._analysis.system_variables[SystemVariable.LABEL],
                    self._analysis.system_variables[SystemVariable.ITERATION],
                }

            case Where():
                return set()

            case Fork(variables, _):
                return {*variables}

            case Gather(aggregates, keys):
                return {
                    # ? [info] basically a virtual key!
                    self._analysis.system_variables[SystemVariable.CONTROL],
                    *aggregates,
                    *keys,
                }

            case _:
                return set()
