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
type Assignment   = CFG.Assignments[Annotation]
type Conditional  = CFG.Conditional[Annotation]
type Emit         = CFG.Emits[Annotation]
type Expression   = common.Expression[Annotation]
type Type         = common.Type[Annotation]
type Identifier   = common.Identifier[Annotation]


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


class LoweringError(errors.PrettyError, ValueError):
    ...


@dataclass
class Lowering:
    _label_prefix: str | None = field(init=False, default=None)
    _nodes: dict[Label, Node] = field(init=False, default_factory=dict)
    _edges: dict[Label, set[Label]] = field(init=False, default_factory=lambda: defaultdict(set))
    _loop_exits: dict[Identifier, list[Label]] = field(init=False, default_factory=lambda: defaultdict(list))
    _label_counters: dict[str, int] = field(init=False, default_factory=lambda: defaultdict(int))

    def _make_label[A](self, name: str, annotation: A) -> common.Identifier[A]:
        self._label_counters[name] += 1
        return common.Identifier(
            f"{name}.{self._label_counters[name]}",
            annotation=annotation
        )

    def lower_function(self, function: parser.Function) -> Function:
        entry_label = self.make_node(
            node=CFG.Source(
                function.name,
                annotation=function.annotation
            ),
            name="entry"
        )

        self.lower_statement(
            predecessors=[entry_label],
            statement=function.body
        )

        graph: Graph = CFG.Graph(
            entry_label=entry_label,
            nodes=self._nodes,
            edges=self._edges,
            annotation=function.body.annotation
        )

        return common.Function(
            name=function.name, # type: ignore
            parameters=function.parameters,
            return_types=function.return_types,
            body=graph,
            annotation=function.annotation
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

    def make_mark(self, predecessor: Label, location: errors.Location) -> Label:
        return self.make_node(
            predecessors=[predecessor],
            node=CFG.Mark(
                annotation=location
            )
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

            case AST.Stop():
                return []

            case AST.Assignment():
                predecessor = self.make_merge(predecessors, statement.annotation)

                this_label = self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Assignments(
                        [statement],
                        annotation=statement.annotation
                    )
                )

                return [this_label]

            case AST.Emit():
                predecessor = self.make_merge(predecessors, statement.annotation)

                this_label = self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Emits(
                        [statement],
                        annotation=statement.annotation
                    )
                )

                return [predecessor]

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
                    node=CFG.Conditional(
                        truthy=[condition],
                        falsey=[],
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
                    node=CFG.Conditional(
                        truthy=[],
                        falsey=[condition],
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
                predecessor = self.make_merge(predecessors, statement.annotation)
                mark_label = self.make_mark(predecessor, statement.annotation)

                source_label = self.make_node(
                    node=CFG.Source(
                        name,
                        annotation=statement.annotation
                    ),
                    name=name.identifier
                )

                loop_labels = self.lower_statement(
                    [mark_label, source_label],
                    body
                )

                for loop_label in loop_labels:
                    self.make_node(
                        predecessors=[loop_label],
                        node=CFG.Sink(
                            name,
                            annotation=statement.annotation
                        ),
                        name="loop"
                    )

                return self._loop_exits[name]

            case AST.Continue(name):
                predecessor = self.make_merge(predecessors, statement.annotation)

                self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Sink(
                        name,
                        annotation=statement.annotation
                    ),
                    name="continue"
                )

                return []

            case AST.Break(name):
                self._loop_exits[name].extend(predecessors)

                return []

            case AST.Sync():
                predecessor = self.make_merge(predecessors, statement.annotation)

                wait_label = self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Wait(
                        annotation=statement.annotation
                    )
                )

                return [wait_label]

            case AST.Fork(variables, expression):
                predecessor = self.make_merge(predecessors, statement.annotation)

                fork_label = self.make_node(
                    predecessors=[predecessor],
                    node=CFG.Fork(
                        variables,
                        expression,
                        annotation=statement.annotation
                    )
                )

                return [fork_label]

            case _:
                raise LoweringError(
                    "Encounted unexpected statement during lowering.",
                    statement.annotation
                )
