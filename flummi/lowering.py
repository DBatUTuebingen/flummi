from collections import defaultdict
from dataclasses import dataclass, field

from .IR import common, AST, CFG

from . import errors, parser


__all__ = (
    "lower",
)

type Annotation   = errors.Location | None
type Program      = CFG.Program[Annotation]
type Function     = CFG.Function[Annotation]
type Handle       = CFG.Handle[Annotation]
type Label        = CFG.Label[Annotation]
type Graph        = CFG.Graph[Annotation]
type Block        = CFG.Block[Annotation]
type Action       = CFG.Action[Annotation]
type Assignments  = CFG.Assignments[Annotation]
type Nothing      = CFG.Nothing[Annotation]
type Wait         = CFG.Wait[Annotation]
type Assignment   = CFG.Assignment[Annotation]
type Terminal     = CFG.Terminal[Annotation]
type TerminalType = CFG.TerminalType[Annotation]
type Call         = CFG.Call[Annotation]
type Return       = CFG.Return[Annotation]
type Jump         = CFG.Jump[Annotation]
type GoTo         = CFG.GoTo[Annotation]
type Expression   = common.Expression[Annotation]
type Type         = common.Type[Annotation]
type Identifier   = common.Identifier[Annotation]


class LoweringError(errors.FlummiError, name="lowering"):
    ...


def lower(program: parser.Program) -> Program:
    function_lists = [
        Lowering().lower_function(function)
        for function in program.function_list
    ]
    return common.Program(
        program.main_function_name,
        program.inputs,
        function_lists,
        annotation=program.annotation
    )


@dataclass
class Lowering:
    _label_prefix: str | None = field(init=False, default=None)
    _current_label: Label = field(init=False)
    _blocks: dict[Label, Block] = field(init=False, default_factory=dict)
    _loop_labels: dict[Identifier, tuple[Label, Label]] = field(init=False, default_factory=dict)
    _variable_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))
    _label_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))
    _function_entry_labels: dict[Identifier, Label] = field(init=False, default_factory=dict)

    def make_label(
        self,
        suffix: str,
        prefix: str | None = None,
        annotation: Annotation = None
    ) -> Label:
        name = (
            f"{prefix}%{suffix}"
            if prefix is not None else
            f"{self._label_prefix}%{suffix}"
            if self._label_prefix is not None else
            suffix
        )
        self._label_counters[name] += 1
        return common.Identifier(
            f"{name}%{self._label_counters[name]}",
            annotation=annotation
        )

    def make_loop_labels(self, loop_name: Identifier) -> tuple[Label, Label]:
        head_label = self.make_label(
            loop_name.identifier + "_head",
            annotation=loop_name.annotation
        )
        exit_label = self.make_label(
            loop_name.identifier + "_exit",
            annotation=loop_name.annotation
        )
        self._loop_labels[loop_name] = (head_label, exit_label)
        return head_label, exit_label

    def new_block(
        self,
        label: Label,
        action: Action | None = None,
        terminals: list[Terminal] | None = None
    ):
        if label in self._blocks:
            raise LoweringError(
                "Tried to produce duplicate block label "
                f"{label.identifier!r}"
            )
        self._blocks[label] = CFG.Block(
            label=label,
            action=action or CFG.Nothing(annotation=None),
            terminals=terminals or [],
            annotation=None
        )

    def add_assignment(
        self,
        label: Label,
        variables: list[Identifier],
        expression: Expression,
        annotation: Annotation = None
    ) -> Label:
        assignment: Assignment = CFG.Assignment(
            variables,
            expression,
            annotation=annotation
        )
        action: Assignments = CFG.Assignments(
            assignments=[assignment],
            annotation=None
        )
        match self._blocks.get(label):
            case None:
                self.new_block(label=label, action=action)
                return label
            case block:
                match block.action:
                    case CFG.Assignments(assignments):
                        assignments.append(assignment)
                        return label
                    case CFG.Nothing:
                        block.action = action
                        return label
                    case _:
                        new_label = self.make_label("assign")
                        self.add_goto(label, new_label)
                        self.new_block(label=new_label, action=action)
                        return new_label

    def add_wait(
        self,
        label: Label,
        handle: Label,
        variables: list[Identifier],
        annotation: Annotation = None
    ) -> CFG.Label:
        wait: Wait = CFG.Wait(
            handle,
            variables,
            annotation=annotation
        )
        match self._blocks.get(label):
            case None:
                self.new_block(label=label, action=wait)
                return label
            case block:
                match block.action:
                    case CFG.Assignments():
                        new_label = self.make_label("wait")
                        self.add_goto(label, new_label)
                        self.new_block(label=new_label, action=wait)
                        return new_label
                    case _:
                        block.action = wait
                        return label

    def add_terminal(
        self,
        label: Label,
        type: TerminalType,
        where: list[Identifier] | None = None,
        where_not: list[Identifier] | None = None,
        annotation: Annotation = None
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
                annotation=annotation
            )
        )

    def add_return(
        self,
        label: Label,
        variables: list[Identifier],
        annotation: Annotation = None
    ):
        self.add_terminal(
            label,
            CFG.Return(variables, annotation=annotation),
        )

    def add_goto(
        self,
        label: Label,
        target: Label,
        where: list[Identifier] | None = None,
        where_not: list[Identifier] | None = None,
        annotation: Annotation = None
    ):
        self.add_terminal(
            label,
            CFG.GoTo(target, annotation=annotation),
            where,
            where_not,
        )

    def add_jump(
        self,
        label: Label,
        target: Label,
        where: list[Identifier] | None = None,
        where_not: list[Identifier] | None = None,
        annotation: Annotation = None
    ):
        self.add_terminal(
            label,
            CFG.Jump(target, annotation=annotation),
            where,
            where_not,
        )

    def add_call(
        self,
        label: Label,
        handle: Label,
        target: Label,
        arguments: list[Identifier],
        annotation: Annotation = None
    ):
        self.add_terminal(
            label,
            CFG.Call(handle, target, arguments, annotation=annotation)
        )

    def _get_loop_labels(self, name: Identifier) -> tuple[Label, Label]:
        return self._loop_labels[name]

    def lower_function(self, function: parser.Function) -> Function:
        self._label_prefix = function.name.identifier
        self.lower_statement(
            label=function.name,
            statement=function.body
        )

        graph: Graph = CFG.Graph(
            entry_label=function.name,
            blocks=self._blocks,
            annotation=function.body.annotation
        )

        return common.Function(
            name=function.name,
            parameters=function.parameters,
            return_types=function.return_types,
            body=graph,
            annotation=function.annotation
        )

    def lower_statement(
        self,
        label: Label,
        statement: parser.Statement
    ) -> Label | None:
        match statement:
            case AST.NoOp():
                return label

            case AST.Return(variables):
                self.add_return(label, variables)

            case AST.Assignment(variables, expression):
                return self.add_assignment(label, variables, expression)

            case AST.Block(statements):
                next_label: CFG.Label | None = label
                for statement in statements:
                    if next_label is not None:
                        next_label = self.lower_statement(next_label, statement)
                return next_label

            case AST.If(condition, truthy_branch, falsey_branch):
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

            case AST.Loop(name, body):
                head_label, exit_label = self.make_loop_labels(name)
                self.add_goto(label, head_label)
                final_body_label = self.lower_statement(head_label, body)
                if final_body_label is not None:
                    self.add_jump(final_body_label, head_label)
                return exit_label

            case AST.Continue(name):
                head_label, _ = self._get_loop_labels(name)
                self.add_jump(label, head_label)
                dead_label = self.make_label("unreachable")
                self.new_block(dead_label)
                return dead_label

            case AST.Break(name):
                _, exit_label = self._get_loop_labels(name)
                self.add_goto(label, exit_label)
                dead_label = self.make_label("unreachable")
                self.new_block(dead_label)
                return dead_label

            case AST.Call(variables, target, arguments):
                handle = self.make_label("call")
                self.add_call(
                    label,
                    handle,
                    target,
                    arguments
                )
                wait_label = self.make_label("wait")
                self.add_goto(label, wait_label)
                return self.add_wait(wait_label, handle, variables)

            case _:
                raise LoweringError(
                    "Found unlowerable statements.",
                    statement.annotation
                )
