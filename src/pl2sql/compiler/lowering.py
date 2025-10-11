from collections import defaultdict
from dataclasses import dataclass, field

from ..IR import common, AST, CFP

from ..library import errors

from . import parser


__all__ = ("lower",)

type Annotation = errors.Location
type Program = CFP.Program[Annotation]
type Label = CFP.Label[Annotation]
type Graph = CFP.Graph[Annotation]
type Node = CFP.Node[Annotation]
type Let = CFP.Let[Annotation]
type Emit = CFP.Emit[Annotation]
type Expression = common.Expression[Annotation]
type Type = common.Type[Annotation]
type Identifier = common.Identifier[Annotation]


def lower(program: parser.Program) -> Graph:
    return Lowering().lower_program(program)


class LoweringError(errors.PrettyError, ValueError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


@dataclass
class Lowering:
    _nodes: dict[Label, Node] = field(init=False, default_factory=dict)
    _edges: dict[Label, set[Label]] = field(
        init=False, default_factory=lambda: defaultdict(set)
    )
    _label_counters: dict[str, int] = field(
        init=False, default_factory=lambda: defaultdict(int)
    )

    def _make_label[A](self, name: str, annotation: A) -> common.Identifier[A]:
        self._label_counters[name] += 1
        return common.Identifier(
            f"{name}.{self._label_counters[name]}",
            annotation=annotation,
        )

    def lower_program(self, program: parser.Program) -> Graph:
        entry_label = common.Identifier("@start", annotation=program.annotation)

        start_node = self.make_node(
            node=CFP.Start(
                annotation=program.annotation,
            ),
            name="start",
        )

        _ = self.lower_statement(start_node, program.body)

        return CFP.Graph(
            entry_label=entry_label,
            nodes=self._nodes,
            edges=self._edges,
            annotation=program.annotation,
        )

    def make_node(
        self,
        node: Node,
        predecessor: Label | None = None,
        name: str | None = None,
    ) -> Label:
        label = self._make_label(
            name or type(node).__name__.lower(), annotation=node.annotation
        )
        self._nodes[label] = node
        self._edges[label] = set()
        if predecessor:
            self._edges[predecessor].add(label)
        return label

    def lower_statement(
        self, predecessor: Label | None, statement: parser.Statement
    ) -> Label | None:
        match statement:
            case AST.NoOp():
                return predecessor

            case AST.Let(variable, expression):
                this_label = self.make_node(
                    predecessor=predecessor,
                    node=CFP.Let(
                        variable=variable,
                        expression=expression,
                        annotation=statement.annotation,
                    ),
                )

                return this_label

            case AST.Stop():
                return

            case AST.Emit(variable):
                this_label = self.make_node(
                    predecessor=predecessor,
                    node=CFP.Emit(
                        variable=variable,
                        annotation=statement.annotation,
                    ),
                )

                return predecessor

            case AST.Block(statements):
                for statement in statements:
                    if predecessor is not None:
                        predecessor = self.lower_statement(
                            predecessor, statement
                        )

                return predecessor
            case _:
                raise LoweringError(
                    "Encounted unexpected statement during lowering.",
                    statement.annotation,
                )
