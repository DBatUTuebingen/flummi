from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Generator
from warnings import warn

from . import CFG, grammar


__all__ = (
    "lower",
)



def lower(program: grammar.Program) -> CFG.Graph:
    return Lowering().lower_program(program)


@dataclass
class Lowering:
    _blocks: dict[CFG.BlockLabel, CFG.Block] = field(init=False, default_factory=dict)
    _loop_labels: dict[str, tuple[CFG.BlockLabel, CFG.BlockLabel]] = field(init=False, default_factory=dict)
    _variable_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))
    _label_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))
    _terminated_blocks: set[CFG.BlockLabel] = field(init=False, default_factory=set)

    def _create_empty_block(self, label: CFG.BlockLabel):
        self._blocks[label] = CFG.Block(
            label=label,
            statements=[],
            terminal=CFG.Stop(),
        )

    def _next_block(self, label: CFG.BlockLabel):
        next_label = self._new_block_label("inter")
        self._terminate_block(label, CFG.GoTo(next_label))
        self._create_empty_block(next_label)
        return next_label

    def _new_variable(self, prefix: str) -> grammar.Variable:
        suffix = str(self._variable_counters[prefix])
        self._variable_counters[prefix] += 1
        return grammar.Variable(
            identifier=prefix + suffix,
        )

    def _new_block_label(self, prefix: str) -> CFG.BlockLabel:
        suffix = str(self._label_counters[prefix])
        self._label_counters[prefix] += 1
        return CFG.BlockLabel(
            label=prefix + suffix
        )

    def _terminate_block(self, label: CFG.BlockLabel, terminal: CFG.Terminal):
        if label not in self._terminated_blocks:
            self._terminated_blocks.add(label)
            self._blocks[label].terminal = terminal

    @contextmanager
    def _new_loop(self, name: str) -> Generator[tuple[CFG.BlockLabel, CFG.BlockLabel], None, None]:
        head_label = CFG.BlockLabel(name + "_head")
        self._create_empty_block(head_label)
        exit_label = CFG.BlockLabel(name + "_exit")
        self._create_empty_block(exit_label)
        self._loop_labels[name] = (head_label, exit_label)
        yield head_label, exit_label

    def _get_loop_labels(self, name: str) -> tuple[CFG.BlockLabel, CFG.BlockLabel]:
        return self._loop_labels[name]

    def lower_program(self, program: grammar.Program) -> CFG.Graph:
        entry_label = CFG.BlockLabel("entry")
        self.lower_function(entry_label, program.function)
        return CFG.Graph(
            entry_label=entry_label,
            blocks=self._blocks,
        )

    def lower_function(self, label: CFG.BlockLabel, function: grammar.Function) -> None:
        self._create_empty_block(label)
        self.lower_statement(label, function.body)

    def lower_statement(self, label: CFG.BlockLabel, statement: grammar.Statement) -> CFG.BlockLabel:
        match statement:
            case grammar.Loop(name, body):
                with self._new_loop(name) as (head_label, exit_label):
                    self._blocks[label].terminal = CFG.GoTo(head_label)
                    final_body_label = self.lower_statement(head_label, body)
                    self._terminate_block(final_body_label, CFG.Jump(head_label))
                    return exit_label

            case grammar.Continue(name):
                head_label, _ = self._get_loop_labels(name)
                self._terminate_block(label, CFG.Jump(head_label))
                return self._next_block(label)

            case grammar.Break(name):
                _, exit_label = self._get_loop_labels(name)
                self._terminate_block(label, CFG.GoTo(exit_label))
                return self._next_block(label)

            case grammar.If(condition, truthy_branch, falsey_branch):
                truthy_label = self._new_block_label("truthy")
                self._create_empty_block(truthy_label)
                falsey_label = self._new_block_label("falsey")
                self._create_empty_block(falsey_label)
                merge_label = self._new_block_label("merge")
                self._create_empty_block(merge_label)

                self._blocks[label].terminal = CFG.If(
                    condition=condition,
                    truthy_terminal=CFG.GoTo(truthy_label),
                    falsey_terminal=CFG.GoTo(falsey_label)
                )

                final_truthy_label = self.lower_statement(truthy_label, truthy_branch)
                self._terminate_block(final_truthy_label, CFG.GoTo(merge_label))

                final_falsey_label = self.lower_statement(falsey_label, falsey_branch)
                self._terminate_block(final_falsey_label, CFG.GoTo(merge_label))

                return merge_label

            case grammar.Emit(to_emit):
                self._blocks[label].statements.append(CFG.Emit(to_emit))
                return self._next_block(label)

            case grammar.Stop():
                self._terminate_block(label, CFG.Stop())
                new_label = self._new_block_label("unreachable")
                self._create_empty_block(new_label)
                return new_label

            case grammar.Assignment(variable, expression):
                self._blocks[label].statements.append(CFG.Assignment(variable, expression))
                return self._next_block(label)

            case grammar.Block(statements):
                for statement in statements:
                    label = self.lower_statement(label, statement)
                return label

            case _:
                warn(f"Found unlowerable construct: {statement}", source="Lowering")
                return label
