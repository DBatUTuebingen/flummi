from dataclasses import dataclass

from ..IR.CFP import (
    Assignment,
    Emit,
    Expression,
    Fork,
    Gather,
    IsSynced,
    Jump,
    Label,
    Primitive,
    Program,
    Start,
    Stop,
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

            case Stop():
                return {
                    self._analysis.system_variables[SystemVariable.CONTROL],
                }

            case Assignment(bindings):
                return {
                    *utils.union(
                        expression.arguments for expression in bindings.values()
                    ),
                }

            case Fork(_, Expression(_, arguments)):
                return set(arguments)

            case Emit(variables):
                return {
                    self._analysis.system_variables[SystemVariable.ITERATION],
                    *variables,
                }

            case Where(variable, _):
                return {variable}

            case Gather(aggregates, keys):
                return keys | {
                    # ? [info] basically a virtual key!
                    self._analysis.system_variables[SystemVariable.CONTROL],
                    *utils.union(
                        expression.arguments
                        for expression in aggregates.values()
                    ),
                }

            case IsSynced(_, _, keys):
                return set(keys)

            case Jump(_):
                return {
                    self._analysis.system_variables[SystemVariable.CONTROL],
                    self._analysis.system_variables[SystemVariable.ITERATION],
                }

            case _:
                return set()

    def binds(self, primitive: Primitive) -> set[Variable]:
        match primitive:
            case Start():
                return {
                    self._analysis.system_variables[SystemVariable.CONTROL],
                    self._analysis.system_variables[SystemVariable.ITERATION],
                }

            case IsSynced(variable, _, _):
                return {variable}

            case Emit(_):
                return {
                    *self._analysis.result_variables,
                    self._analysis.system_variables[SystemVariable.ITERATION],
                }

            case Jump():
                return {
                    self._analysis.system_variables[SystemVariable.LABEL],
                    self._analysis.system_variables[SystemVariable.ITERATION],
                }

            case Fork(variables, _):
                return set(variables)

            case Gather(bindings, _):
                return {
                    # ? [info] basically a virtual key!
                    self._analysis.system_variables[SystemVariable.CONTROL],
                    *bindings,
                }

            case Assignment(bindings):
                return {*bindings}

            case _:
                return set()
