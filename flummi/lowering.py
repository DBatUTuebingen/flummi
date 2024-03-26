from collections import defaultdict
from dataclasses import dataclass, field

from . import CFG, grammar, errors


__all__ = (
    "lower",
)


class LoweringError(errors.FlummiError, name="lowering"):
    ...


def lower(program: grammar.Program) -> CFG.Graph:
    return Lowering().lower_program(program)


@dataclass
class Lowering:
    _label_prefix: str | None = field(init=False, default=None)
    _current_label: CFG.Label = field(init=False)
    _blocks: dict[CFG.Label, CFG.Block] = field(init=False, default_factory=dict)
    _loop_labels: dict[grammar.Variable, tuple[CFG.Label, CFG.Label]] = field(init=False, default_factory=dict)
    _variable_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))
    _label_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))
    _function_entry_labels: dict[grammar.Variable, CFG.Label] = field(init=False, default_factory=dict)

    def make_label(self, suffix: str, prefix: str | None = None) -> CFG.Label:
        name = (
            f"{prefix}%{suffix}"
            if prefix is not None else
            f"{self._label_prefix}%{suffix}"
            if self._label_prefix is not None else
            suffix
        )
        self._label_counters[name] += 1
        return CFG.Label(f"{name}%{self._label_counters[name]}")

    def make_loop_labels(self, name: grammar.Variable) -> tuple[CFG.Label, CFG.Label]:
        head_label = self.make_label(name.identifier + "_head")
        exit_label = self.make_label(name.identifier + "_exit")
        self._loop_labels[name] = (head_label, exit_label)
        return head_label, exit_label

    def new_block(
        self,
        label: CFG.Label,
        action: CFG.Action | None = None,
        terminals: list[CFG.Terminal] | None = None
    ):
        if label in self._blocks:
            raise LoweringError(
                "Tried to produce duplicate block label "
                f"{label.label!r}"
            )
        self._blocks[label] = CFG.Block(
            label=label,
            action=action or CFG.Nothing(),
            terminals=terminals or []
        )

    def add_assignment(
        self,
        label: CFG.Label,
        variables: list[grammar.Variable],
        expression: grammar.Expression
    ) -> CFG.Label:
        assignment = CFG.Assignment(variables, expression)
        match self._blocks.get(label):
            case None:
                self.new_block(
                    label=label,
                    action=CFG.Assignments([assignment]),
                )
                return label
            case block:
                match block.action:
                    case CFG.Assignments(assignments):
                        assignments.append(assignment)
                        return label
                    case CFG.Nothing:
                        block.action = CFG.Assignments([assignment])
                        return label
                    case _:
                        new_label = self.make_label("assign")
                        self.add_goto(label, new_label)
                        self.new_block(
                            label=new_label,
                            action=CFG.Assignments([assignment]),
                        )
                        return new_label

    def add_wait(
        self,
        label: CFG.Label,
        handle: CFG.Label,
        variables: list[grammar.Variable],
    ) -> CFG.Label:
        wait = CFG.Wait(handle, variables)
        match self._blocks.get(label):
            case None:
                self.new_block(
                    label=label,
                    action=wait,
                )
                return label
            case block:
                match block.action:
                    case CFG.Assignments():
                        new_label = self.make_label("wait")
                        self.add_goto(label, new_label)
                        self.new_block(
                            label=new_label,
                            action=wait,
                        )
                        return new_label
                    case _:
                        block.action = wait
                        return label

    def add_terminal(
        self,
        label: CFG.Label,
        type: CFG.TerminalType,
        where: list[grammar.Variable] | None = None,
        where_not: list[grammar.Variable] | None = None
    ):
        block = self._blocks.get(label)
        if block is None:
            self.new_block(label)
            block = self._blocks[label]
        block.terminals.append(
            CFG.Terminal(
                type=type,
                truthy=where or [],
                falsey=where_not or [],
            )
        )

    def add_return(
        self,
        label: CFG.Label,
        variables: list[grammar.Variable],
    ):
        self.add_terminal(
            label,
            CFG.Return(variables)
        )

    def add_goto(
        self,
        label: CFG.Label,
        target: CFG.Label,
        where: list[grammar.Variable] | None = None,
        where_not: list[grammar.Variable] | None = None
    ):
        self.add_terminal(
            label,
            CFG.GoTo(target),
            where,
            where_not
        )

    def add_jump(
        self,
        label: CFG.Label,
        target: CFG.Label,
        where: list[grammar.Variable] | None = None,
        where_not: list[grammar.Variable] | None = None
    ):
        self.add_terminal(
            label,
            CFG.Jump(target),
            where,
            where_not
        )

    def add_call(
        self,
        label: CFG.Label,
        handle: CFG.Label,
        target: CFG.Label,
        arguments: list[grammar.Variable]
    ):
        self.add_terminal(
            label,
            CFG.Call(handle, target, arguments)
        )

    def _get_loop_labels(self, name: grammar.Variable) -> tuple[CFG.Label, CFG.Label]:
        return self._loop_labels[name]

    def lower_program(self, program: grammar.Program) -> CFG.Graph:
        self.function_entry_labels = {
            function.name:
            self.make_label("entry", prefix=function.name.identifier)
            for function in program.function_list
        }

        for function in program.function_list:
            self.lower_function(function)

        return CFG.Graph(
            entry_label=self.function_entry_labels[program.main_function_name],
            initialising_assignment=CFG.Assignment(
                list(program.main_function.parameters),
                program.inputs
            ) if program.inputs is not None else None,
            blocks=self._blocks,
        )

    def lower_function(self, function: grammar.Function) -> None:
        self._label_prefix = function.name.identifier
        self.lower_statement(
            self.function_entry_labels[function.name],
            function.body
        )

    def lower_statement(
        self,
        label: CFG.Label,
        statement: grammar.Statement
    ) -> CFG.Label | None:
        match statement:
            case grammar.NoOp():
                return label

            case grammar.Return(_, variables):
                self.add_return(label, variables)

            case grammar.Assignment(_, variables, expression):
                return self.add_assignment(label, variables, expression)

            case grammar.Block(_, statements):
                next_label: CFG.Label | None = label
                for statement in statements:
                    if next_label is not None:
                        next_label = self.lower_statement(next_label, statement)
                return next_label

            case grammar.If(_, condition, truthy_branch, falsey_branch):
                truthy_label = self.make_label("truthy")
                self.add_goto(
                    label,
                    truthy_label,
                    where=[condition]
                )
                final_truthy_label =\
                    self.lower_statement(truthy_label, truthy_branch)

                falsey_label = self.make_label("falsey")
                self.add_goto(
                    label,
                    falsey_label,
                    where_not=[condition]
                )
                final_falsey_label =\
                    self.lower_statement(falsey_label, falsey_branch)

                merge_label = self.make_label("merge")
                if final_truthy_label is not None:
                    self.add_goto(final_truthy_label, merge_label)
                if final_falsey_label is not None:
                    self.add_goto(final_falsey_label, merge_label)

                return merge_label

            case grammar.Loop(_, name, body):
                head_label, exit_label = self.make_loop_labels(name)
                self.add_goto(label, head_label)
                final_body_label = self.lower_statement(head_label, body)
                if final_body_label is not None:
                    self.add_jump(final_body_label, head_label)
                return exit_label

            case grammar.Continue(_, name):
                head_label, _ = self._get_loop_labels(name)
                self.add_jump(label, head_label)
                dead_label = self.make_label("unreachable")
                self.new_block(dead_label)
                return dead_label

            case grammar.Break(_, name):
                _, exit_label = self._get_loop_labels(name)
                self.add_goto(label, exit_label)
                dead_label = self.make_label("unreachable")
                self.new_block(dead_label)
                return dead_label

            case grammar.Call(_, variables, target, arguments):
                handle = self.make_label("call")
                self.add_call(
                    label,
                    handle,
                    self.function_entry_labels[target],
                    arguments
                )
                wait_label = self.make_label("wait")
                self.add_goto(label, wait_label)
                return self.add_wait(wait_label, handle, variables)

            case _:
                raise LoweringError(
                    "Found unlowerable statements.",
                    statement.location
                )
