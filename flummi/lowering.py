from collections import defaultdict
from dataclasses import dataclass, field
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
    _label_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))

    def _new_label(self, prefix: str) -> CFG.BlockLabel:
        i = self._label_counters[prefix]
        self._label_counters[prefix] += 1
        return CFG.BlockLabel(label=f"{prefix}%{i}")

    def _add_block(
        self,
        prefix: str,
        *,
        action: CFG.Action | None = None,
        terminals: list[CFG.Terminal] | None = None
    ) -> CFG.BlockLabel:
        label = self._new_label(prefix)
        self._blocks[label] = CFG.Block(label, action, terminals or [])
        return label

    def _add_goto(
        self,
        from_label: CFG.BlockLabel,
        to_label: CFG.BlockLabel,
        when: grammar.Variable | None = None,
        when_not: grammar.Variable | None = None
    ):
        self._blocks[from_label].terminals.append(
            CFG.Terminal(
                CFG.GoTo(to_label),
                [when] if when else [],
                [when_not] if when_not else []
            )
        )

    def _add_emit(
        self,
        from_label: CFG.BlockLabel,
        emit: grammar.Emit
    ):
        self._blocks[from_label].terminals.append(
            CFG.Terminal(CFG.Emit(emit), [], [])
        )

    def _add_assignment(
        self,
        label: CFG.BlockLabel,
        assignment: grammar.Assignment
    ):
        if any(argument.valuedness == grammar.Valuedness.SET for argument in assignment.expression.arguments):
            action = CFG.ReducingAssignment(assignment)
        else:
            action = CFG.SpanningAssignments([assignment])
        self._blocks[label].action = action

    def lower_program(self, program: grammar.Program) -> CFG.Graph:
        label = self._add_block("entry")
        if program.inputs is not None:
            self._add_assignment(label, grammar.Assignment(program.location, list(program.function.parameters), program.inputs))
        self.lower_statement(label, program.function.body)
        return CFG.Graph(
            entry_label=label,
            blocks=self._blocks,
        )

    def lower_statement(self, label: CFG.BlockLabel, statement: grammar.Statement) -> CFG.BlockLabel:
        match statement:
            case grammar.Stop(_):
                unreachable_label = self._add_block("unreachable")
                return unreachable_label

            case grammar.Block(_, statements):
                for statement in statements:
                    label = self.lower_statement(label, statement)
                return label

            case grammar.Assignment(_, _, _):
                assignment_label = self._add_block("assignment")
                self._add_assignment(assignment_label, statement)
                self._add_goto(label, assignment_label)
                return assignment_label

            case grammar.Emit(_, _):
                emit_label = self._add_block("emit")
                self._add_emit(emit_label, statement)
                self._add_goto(label, emit_label)
                return emit_label

            case grammar.If(_, condition, truthy_branch, falsey_branch):
                truthy_label = self._add_block("truthy")
                self._add_goto(label, truthy_label, when=condition)
                final_truthy_label = self.lower_statement(truthy_label, truthy_branch)

                falsey_label = self._add_block("falsey")
                self._add_goto(label, falsey_label, when_not=condition)
                final_falsey_label = self.lower_statement(falsey_label, falsey_branch)

                merge_label = self._add_block("merge")
                self._add_goto(final_truthy_label, merge_label)
                self._add_goto(final_falsey_label, merge_label)
                return merge_label

            case _:
                warn(f"Found unlowerable construct: {statement}", source="Lowering")
                return label
