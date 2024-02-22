from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Generator
from warnings import warn

from . import CFG, grammar


__all__ = (
    "lower",
)


def lower(program: grammar.Program) -> tuple[CFG.Graph, set[grammar.Variable], set[grammar.Variable]]:
    return Lowering().lower_program(program)


@dataclass
class Lowering:
    _blocks: dict[CFG.BlockLabel, CFG.Block] = field(init=False, default_factory=dict)
    _loop_labels: dict[str, tuple[CFG.BlockLabel, CFG.BlockLabel]] = field(init=False, default_factory=dict)
    _variable_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))
    _label_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))
    _condition_variables: set[grammar.Variable] = field(init=False, default_factory=set)
    _emit_variables: set[grammar.Variable] = field(init=False, default_factory=set)

    def _create_empty_block(self, label: CFG.BlockLabel):
        self._blocks[label] = CFG.Block(
            label=label,
            assignments=[],
            terminals=[],
        )

    def _next_block(self, label: CFG.BlockLabel | None = None, prefix: str | None = None):
        next_label = self._new_block_label(prefix or "inter")
        if label:
            self._blocks[label].terminals.append(CFG.Terminal(type=CFG.GoTo(next_label)))
        self._create_empty_block(next_label)
        return next_label

    def _new_variable(self, prefix: str) -> grammar.Variable:
        suffix = str(self._variable_counters[prefix])
        self._variable_counters[prefix] += 1
        return grammar.Variable(identifier=prefix + "%" + suffix)

    def _new_block_label(self, prefix: str) -> CFG.BlockLabel:
        suffix = str(self._label_counters[prefix])
        self._label_counters[prefix] += 1
        return CFG.BlockLabel(label=prefix + suffix)

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

    def lower_program(self, program: grammar.Program) -> tuple[CFG.Graph, set[grammar.Variable], set[grammar.Variable]]:
        entry_label = CFG.BlockLabel("entry")
        self.lower_function(entry_label, program.function)
        return CFG.Graph(
            entry_label=entry_label,
            blocks=self._blocks,
        ), self._condition_variables, self._emit_variables

    def lower_function(self, label: CFG.BlockLabel, function: grammar.Function) -> None:
        self._create_empty_block(label)
        self.lower_statement(label, function.body)

    def lower_statement(self, label: CFG.BlockLabel, statement: grammar.Statement) -> CFG.BlockLabel:
        match statement:
            case grammar.Loop(name, body):
                with self._new_loop(name) as (head_label, exit_label):
                    self._blocks[label].terminals.append(CFG.Terminal(type=CFG.GoTo(head_label)))
                    final_body_label = self.lower_statement(head_label, body)
                    self._blocks[final_body_label].terminals.append(CFG.Terminal(type=CFG.Jump(head_label)))
                    return exit_label

            case grammar.Continue(name):
                head_label, _ = self._get_loop_labels(name)
                self._blocks[label].terminals.append(CFG.Terminal(type=CFG.Jump(head_label)))
                return self._next_block()

            case grammar.Break(name):
                _, exit_label = self._get_loop_labels(name)
                self._blocks[label].terminals.append(CFG.Terminal(type=CFG.GoTo(exit_label)))
                return self._next_block()

            case grammar.If(condition, truthy_branch, falsey_branch):
                condition_var = self._new_variable("cond")
                self._condition_variables.add(condition_var)
                self._blocks[label].assignments.append(CFG.Assignment(condition_var, condition))

                truthy_label = self._new_block_label("truthy")
                self._create_empty_block(truthy_label)
                self._blocks[label].terminals.append(CFG.Terminal(type=CFG.GoTo(truthy_label), truthy=[condition_var]))
                final_truthy_label = self.lower_statement(truthy_label, truthy_branch)

                falsey_label = self._new_block_label("falsey")
                self._create_empty_block(falsey_label)
                self._blocks[label].terminals.append(CFG.Terminal(type=CFG.GoTo(falsey_label), falsey=[condition_var]))
                final_falsey_label = self.lower_statement(falsey_label, falsey_branch)

                merge_label = self._new_block_label("merge")
                self._create_empty_block(merge_label)
                self._blocks[final_truthy_label].terminals.append(CFG.Terminal(type=CFG.GoTo(merge_label)))
                self._blocks[final_falsey_label].terminals.append(CFG.Terminal(type=CFG.GoTo(merge_label)))

                return merge_label

            case grammar.Emit(to_emit):
                emit_var = self._new_variable("emit")
                self._emit_variables.add(emit_var)
                self._blocks[label].assignments.append(CFG.Assignment(emit_var, to_emit))
                self._blocks[label].terminals.append(CFG.Terminal(type=CFG.Emit(emit_var)))
                return self._next_block(label)

            case grammar.Stop():
                return self._next_block(prefix="unreachable")

            case grammar.Assignment(variable, expression):
                self._blocks[label].assignments.append(CFG.Assignment(variable, expression))
                return self._next_block(label)

            case grammar.Block(statements):
                for statement in statements:
                    label = self.lower_statement(label, statement)
                return label

            case _:
                warn(f"Found unlowerable construct: {statement}", source="Lowering")
                return label
