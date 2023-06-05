from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from typing import Generic, Generator, TypeVar
from warnings import warn

from .grammars import proc, common, CFG


__all__ = (
    "lower",
)


E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


def lower(program: proc.Program[E, T], boolean_type: T) -> CFG.Graph[E, T]:
    return Lowering(common.Type(boolean_type)).lower_program(program)


class LoweringWarning(UserWarning):
    ...


class LoweringError(Exception):
    ...


@dataclass
class Lowering(Generic[E, T]):
    boolean_type: common.Type[T]
    _emit_type: common.Type[T] = field(init=False)
    _blocks: dict[CFG.BlockLabel, CFG.Block[E]] = field(init=False, default_factory=dict)
    _terminated_blocks: set[CFG.BlockLabel] = field(init=False, default_factory=set)
    _loop_labels: list[tuple[CFG.BlockLabel, CFG.BlockLabel]] = field(init=False, default_factory=list)
    _variable_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))
    _label_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))
    _variables: dict[common.Variable, common.Type[T]] = field(init=False, default_factory=dict)

    def _create_empty_block(self, label: CFG.BlockLabel):
        self._blocks[label] = CFG.Block(
            label=label,
            parameters=[],
            statements=[],
            terminal=CFG.Stop(),
            predecessor_references=[],
        )

    def _chain_statements(self, label: CFG.BlockLabel, *statements: CFG.Statement[E]):
        for statement in statements:
            self._blocks[label].statements.append(statement)
            next_label = self._new_block_label("inter")
            self._terminate_block(label, CFG.GoTo(next_label, []))
            self._create_empty_block(next_label)
            label = next_label
        return label

    def _terminate_block(self, label: CFG.BlockLabel, terminal: CFG.Terminal):
        if label not in self._terminated_blocks:
            self._blocks[label].terminal = terminal
            self._terminated_blocks.add(label)

    def _new_variable(self, prefix: str) -> common.Variable:
        suffix = str(self._variable_counters[prefix])
        self._variable_counters[prefix] += 1
        return common.Variable(
            identifier=prefix + suffix,
        )

    def _new_block_label(self, prefix: str) -> CFG.BlockLabel:
        suffix = str(self._label_counters[prefix])
        self._label_counters[prefix] += 1
        return CFG.BlockLabel(
            label=prefix + suffix
        )

    def _add_program_variable(self, variable: common.Variable, type: common.Type[T]):
        if variable in self._variables:
            raise LoweringError("Tried to redeclare an already declared variable.")
        self._variables[variable] = type

    @contextmanager
    def _new_loop(self) -> Generator[tuple[CFG.BlockLabel, CFG.BlockLabel], None, None]:
        loop_label = self._new_block_label("loop")
        head_label = replace(loop_label, label=loop_label.label + "_head")
        self._create_empty_block(head_label)
        exit_label = replace(loop_label, label=loop_label.label + "_exit")
        self._create_empty_block(exit_label)
        self._loop_labels.append((head_label, exit_label))
        yield head_label, exit_label
        self._loop_labels.pop()

    def _latest_loop_labels(self) -> tuple[CFG.BlockLabel, CFG.BlockLabel]:
        return self._loop_labels[-1]

    def lower_program(self, program: proc.Program[E, T]) -> CFG.Graph[E, T]:
        entry_label = CFG.BlockLabel("entry")
        self.lower_function(entry_label, program.function)
        return CFG.Graph(
            entry_label=entry_label,
            inputs=dict(zip(program.function.parameters, program.inputs)),
            emits=program.function.emits,
            variables=self._variables,
            blocks=self._blocks,
            jumps=[]
        )

    def lower_function(self, label: CFG.BlockLabel, function: proc.Function[E, T]) -> None:
        self._emit_type = function.emits
        for parameter, type in function.parameters.items():
            self._add_program_variable(parameter, type)
        self._create_empty_block(label)
        self.lower_statement(label, function.body)

    def lower_statement(self, label: CFG.BlockLabel, statement: proc.Statement[E, T]) -> CFG.BlockLabel:
        match statement:
            case proc.Loop(body):
                with self._new_loop() as (head_label, exit_label):
                  self._terminate_block(
                      label,
                      CFG.GoTo(
                          label=head_label,
                          arguments=[]
                      )
                  )

                  final_body_label = self.lower_statement(head_label, body)

                  self._terminate_block(
                      final_body_label,
                      CFG.GoTo(
                          label=head_label,
                          arguments=[]
                      )
                  )

                  return exit_label

            case proc.Continue():
                head_label, _ = self._latest_loop_labels()
                self._terminate_block(
                    label,
                    CFG.GoTo(
                        label=head_label,
                        arguments=[]
                    )
                )
                return label

            case proc.Break():
                _, exit_label = self._latest_loop_labels()
                self._terminate_block(
                    label,
                    CFG.GoTo(
                        label=exit_label,
                        arguments=[]
                    )
                )
                return label

            case proc.If(condition, truthy_branch, falsey_branch):
                condition_variable = self._new_variable("condition%")
                self._add_program_variable(condition_variable, self.boolean_type)
                truthy_label = self._new_block_label("truthy")
                self._create_empty_block(truthy_label)
                falsey_label = self._new_block_label("falsey")
                self._create_empty_block(falsey_label)
                merge_label = self._new_block_label("merge")
                self._create_empty_block(merge_label)

                label = self._chain_statements(
                    label,
                    CFG.Assignment(
                        variable=condition_variable,
                        expression=condition,
                    )
                )

                self._terminate_block(
                    label,
                    CFG.If(
                        condition=condition_variable,
                        truthy_terminal=CFG.GoTo(
                            label=truthy_label,
                            arguments=[],
                        ),
                        falsey_terminal=CFG.GoTo(
                            label=falsey_label,
                            arguments=[],
                        )
                    )
                )

                final_truthy_label = self.lower_statement(truthy_label, truthy_branch)
                self._terminate_block(
                    final_truthy_label,
                    CFG.GoTo(
                        label=merge_label,
                        arguments=[]
                    )
                )

                final_falsey_label = self.lower_statement(falsey_label, falsey_branch)
                self._terminate_block(
                    final_falsey_label,
                    CFG.GoTo(
                        label=merge_label,
                        arguments=[]
                    )
                )

                return merge_label

            case proc.Emit(to_emit):
                return self._chain_statements(
                    label,
                    CFG.Emit(to_emit=to_emit)
                )

            case proc.Stop():
                self._terminate_block(label, CFG.Stop())
                label = self._new_block_label("unreachable")
                self._create_empty_block(label)
                return label

            case proc.Declaration(variable, type):
                self._add_program_variable(variable, type)
                return label

            case proc.Assignment(variable, expression):
                return self._chain_statements(
                    label,
                    CFG.Assignment(
                        variable=variable,
                        expression=expression,
                    ),
                )

            case proc.Block(statements):
                for statement in statements:
                    label = self.lower_statement(label, statement)
                return label

            case _:
                warn(LoweringWarning(f"Unknown construct: {statement}"))
                return label
