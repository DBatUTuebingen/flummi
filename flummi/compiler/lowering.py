from collections import defaultdict
from dataclasses import dataclass, field

from ..IR import common, AST, CFG

from ..library import errors

from . import parser


__all__ = (
    "lower",
)

type Annotation   = errors.Location
type Program      = CFG.Program[Annotation]
type Function     = CFG.Function[Annotation]
type Label        = CFG.Label[Annotation]
type Graph        = CFG.Graph[Annotation]
type Node         = CFG.Node[Annotation]
type Let          = CFG.Let[Annotation]
type Where        = CFG.Where[Annotation]
type WhereNot     = CFG.WhereNot[Annotation]
type Return       = CFG.Return[Annotation]
type Push         = CFG.Push[Annotation]
type Pop          = CFG.Pop[Annotation]
type Link         = CFG.Link[Annotation]
type Resume       = CFG.Resume[Annotation]
type Lookup       = CFG.Lookup[Annotation]
type Memoize      = CFG.Memoize[Annotation]
type Expression   = common.Expression[Annotation]
type Type         = common.Type[Annotation]
type Identifier   = common.Identifier[Annotation]


def lower(program: parser.Program) -> Graph:
    return Lowering().lower_program(program)


class LoweringError(errors.PrettyError, ValueError):
    ...


@dataclass
class Lowering:
    _return_from: Identifier = field(init=False)
    _label_prefix: str = field(init=False, default_factory=str)
    _nodes: dict[Label, Node] = field(init=False, default_factory=dict)
    _edges: dict[Label, set[Label]] = field(init=False, default_factory=lambda: defaultdict(set))
    _loop_exits: dict[Identifier, list[Label]] = field(init=False, default_factory=lambda: defaultdict(list))
    _label_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))

    def _make_label[A](self, name: str, annotation: A) -> common.Identifier[A]:
        self._label_counters[name] += 1
        return common.Identifier(
            f"{self._label_prefix}.{name}.{self._label_counters[name]}",
            annotation=annotation
        )

    def lower_program(self, program: parser.Program) -> Graph:
        entry_label = common.Identifier(
            "@program",
            annotation=program.annotation
        )

        start_node = self.make_node(
            node=CFG.Pop(
                common.Identifier(
                    "@program",
                    annotation=program.annotation
                ),
                annotation=program.annotation
            ),
            name="program"
        )

        self._return_from = common.Identifier(
            "@program",
            annotation=program.annotation
        )

        self.lower_statement([start_node], program.statement)

        for function in program.function_list:
            self.lower_function(function)

        return CFG.Graph(
            entry_label=entry_label,
            nodes=self._nodes,
            edges=self._edges,
            annotation=program.annotation
        )

    def lower_function(self, function: parser.Function) -> None:
        self._return_from = function.name

        self._label_prefix = function.name.identifier

        entry_label = self.make_node(
            node=CFG.Pop(
                function.name,
                annotation=function.annotation
            ),
            name="function"
        )

        self.lower_statement(
            predecessors=[entry_label],
            statement=function.body
        )

    def make_node(
        self,
        node: Node,
        predecessors: list[Label] | None = None,
        name: str | None = None
    ) -> Label:
        label = self._make_label(
            name or type(node).__name__.lower(),
            annotation=node.annotation
        )
        self._nodes[label] = node
        self._edges[label] = set()
        if predecessors:
            for predecessor in predecessors:
                self._edges[predecessor].add(label)
        return label

    def make_merge(self, predecessors: list[Label], location: errors.Location) -> Label:
        if len(predecessors) > 1:
            return self.make_node(
                predecessors=predecessors,
                node=CFG.Merge(
                    annotation=location
                )
            )
        elif len(predecessors) == 1:
            return predecessors[0]
        else:
            raise LoweringError(
                "Tried to create a merge node with no predecessors.",
                location
            )

    def lower_statement(
        self,
        predecessors: list[Label],
        statement: parser.Statement
    ) -> list[Label]:
        if len(predecessors) == 0:
            raise LoweringError(
                "Tried to lower statement without any predecessors.",
                statement.annotation
            )

        match statement:
            case AST.NoOp():
                return predecessors

            case AST.Let(variable, expression):
                predecessor = self.make_merge(predecessors, statement.annotation)

                this_label = self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Let(
                        variable=variable,
                        expression=expression,
                        annotation=statement.annotation
                    )
                )

                return [this_label]

            case AST.Return(variable):
                predecessor = self.make_merge(predecessors, statement.annotation)

                this_label = self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Return(
                        function=self._return_from,
                        variable=variable,
                        annotation=statement.annotation
                    )
                )

                return []

            case AST.Block(statements):
                for statement in statements:
                    if predecessors:
                        predecessors = self.lower_statement(
                            predecessors,
                            statement
                        )

                return predecessors

            case AST.If(condition, truthy_branch, falsey_branch):
                predecessor = self.make_merge(predecessors, statement.annotation)

                truthy_label = self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Where(
                        variable=condition,
                        annotation=statement.annotation
                    ),
                    name="truthy"
                )
                final_truthy_label = self.lower_statement(
                    [truthy_label],
                    truthy_branch
                )

                falsey_label = self.make_node(
                    predecessors=[predecessor],
                    node=CFG.WhereNot(
                        variable=condition,
                        annotation=statement.annotation
                    ),
                    name="falsey"
                )
                final_falsey_label = self.lower_statement(
                    [falsey_label],
                    falsey_branch
                )

                return final_truthy_label + final_falsey_label

            case AST.Loop(name, body):
                pop_label = self.make_node(
                    node=CFG.Pop(
                        name,
                        annotation=statement.annotation
                    ),
                    name="loop_head"
                )

                loop_labels = self.lower_statement(
                    predecessors + [pop_label],
                    body
                )

                for loop_label in loop_labels:
                    self.make_node(
                        predecessors=[loop_label],
                        node=CFG.Push(
                            name,
                            annotation=statement.annotation
                        ),
                        name="loop_back"
                    )

                return self._loop_exits[name]

            case AST.Continue(name):
                predecessor = self.make_merge(predecessors, statement.annotation)

                self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Push(
                        name,
                        annotation=statement.annotation
                    ),
                    name="continue"
                )

                return []

            case AST.Break(name):
                self._loop_exits[name].extend(predecessors)

                return []

            case AST.Call(function, arguments, variable):
                predecessor = self.make_merge(predecessors, statement.annotation)

                callsite = self._make_label("@callsite", annotation=statement.annotation)

                self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Push(
                        callsite,
                        annotation=statement.annotation
                    ),
                    name="suspend",
                )

                link_label = self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Link(
                        callsite,
                        annotation=statement.annotation
                    )
                )

                self.lower_statement(
                    [link_label],
                    AST.TailCall(
                        function,
                        arguments,
                        annotation=statement.annotation
                    )
                )

                pop_label = self.make_node(
                    node=CFG.Pop(
                        callsite,
                        annotation=statement.annotation
                    ),
                    name="awake"
                )

                resume_label = self.make_node(
                    predecessors=[pop_label],
                    node=CFG.Resume(
                        function,
                        variable,
                        annotation=statement.annotation
                    )
                )

                return [resume_label]

            case AST.TailCall(function, arguments):
                predecessor = self.make_merge(predecessors, statement.annotation)

                predecessors = self.lower_statement(
                    [predecessor],
                    AST.Block(
                        statements=[
                            AST.Let(
                                parameter,
                                common.Expression(
                                    "{0}",
                                    arguments=[argument],
                                    annotation=argument.annotation
                                ),
                                annotation=parameter.annotation
                            )
                            for parameter, argument in arguments.items()
                        ],
                        annotation=statement.annotation
                    )
                )

                assert len(predecessors) == 1

                self.make_node(
                    predecessors=predecessors,
                    node=CFG.Push(
                        function,
                        annotation=statement.annotation
                    ),
                    name="call"
                )

                return []

            case AST.Lookup(result, hit, function, arguments):
                predecessor = self.make_merge(predecessors, statement.annotation)

                lookup_label = self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Lookup(
                        result,
                        hit,
                        function,
                        arguments,
                        annotation=statement.annotation
                    )
                )

                return [lookup_label]

            case AST.Memoize(function, arguments, value):
                predecessor = self.make_merge(predecessors, statement.annotation)

                memoize_label = self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Memoize(
                        function,
                        arguments,
                        value,
                        annotation=statement.annotation
                    )
                )

                return [predecessor]

            case _:
                raise LoweringError(
                    "Encounted unexpected statement during lowering.",
                    statement.annotation
                )
