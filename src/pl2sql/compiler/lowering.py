from collections import defaultdict
from dataclasses import dataclass, field

from ..IR import common, AST, CFP

from ..library import errors, graph


__all__ = ("lower",)


def lower(program: AST.Program) -> CFP.Program:
    return Lowering().lower_program(program)


class LoweringError(errors.PrettyError, ValueError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


@dataclass
class Lowering:
    _primitives: dict[CFP.Label, CFP.Primitive] = field(
        init=False, default_factory=dict
    )
    _edges: dict[CFP.Label, set[CFP.Label]] = field(
        init=False, default_factory=lambda: defaultdict(set)
    )
    _label_counters: dict[str, int] = field(
        init=False, default_factory=lambda: defaultdict(int)
    )

    def _make_label(
        self, name: str, location: errors.Location
    ) -> common.Identifier:
        self._label_counters[name] += 1
        return common.Identifier(
            f"{name}.{self._label_counters[name]}",
            location=location,
        )

    def add_merge(
        self, predecessors: list[CFP.Label], location: errors.Location
    ) -> CFP.Label:
        if len(predecessors) > 1:
            label = self.add_primitive(CFP.Merge(location=location))
            for predecessor in predecessors:
                self.add_edge(predecessor, label)
            return label
        elif len(predecessors) == 1:
            return predecessors[0]
        else:
            raise LoweringError(
                "Tried to create a merge primtiive with no predecessors.",
                location,
            )

    def lower_program(self, program: AST.Program) -> CFP.Program:
        entry_label = self.add_primitive(
            primitive=CFP.Start(
                location=program.location,
            ),
            name="start",
        )

        _ = self.lower_statement([entry_label], program.body)

        predecessors = graph.invert(self._edges)

        for label, primitive in self._primitives.items():
            multiple_predecessors = len(predecessors[label]) > 1
            is_merge = isinstance(primitive, CFP.Merge)
            if is_merge != multiple_predecessors:
                raise LoweringError(
                    "Produced multi-predecessor non-merge primitives!",
                    primitive.location,
                )

        cfp = CFP.Graph(
            primitives=self._primitives,
            transitions=self._edges,
            location=program.location,
        )

        return CFP.Program(body=cfp, location=program.location)

    def add_primitive(
        self,
        primitive: CFP.Primitive,
        name: str | None = None,
    ) -> CFP.Label:
        label = self._make_label(
            name or type(primitive).__name__.lower(),
            location=primitive.location,
        )
        self._primitives[label] = primitive
        self._edges[label] = set()
        return label

    def add_edge(self, source: CFP.Label, sink: CFP.Label):
        self._edges[source].add(sink)

    def lower_statement(
        self, predecessors: list[CFP.Label], statement: AST.Statement
    ) -> list[CFP.Label]:
        match statement:
            case AST.NoOp():
                return predecessors

            case AST.Let(variable, expression):
                predecessor = self.add_merge(predecessors, statement.location)

                this_label = self.add_primitive(
                    CFP.Let(
                        variable=variable,
                        expression=expression,
                        location=statement.location,
                    ),
                )

                self.add_edge(predecessor, this_label)

                return [this_label]

            case AST.Stop():
                return []

            case AST.Emit(variable):
                for predecessor in predecessors:
                    emit_label = self.add_primitive(
                        primitive=CFP.Emit(
                            variable=variable,
                            location=statement.location,
                        ),
                    )

                    self.add_edge(predecessor, emit_label)

                return predecessors

            case AST.Block(statements):
                for statement in statements:
                    if not predecessors:
                        break

                    predecessors = self.lower_statement(predecessors, statement)

                return predecessors

            case AST.If(condition, truthy_branch, falsey_branch):
                predecessor = self.add_merge(predecessors, statement.location)

                where_label = self.add_primitive(
                    CFP.Where(condition, location=statement.location)
                )
                where_not_label = self.add_primitive(
                    CFP.WhereNot(condition, location=statement.location)
                )
                self.add_edge(predecessor, where_label)
                self.add_edge(predecessor, where_not_label)

                truthy_labels = self.lower_statement(
                    [where_label], truthy_branch
                )
                falsey_labels = self.lower_statement(
                    [where_not_label], falsey_branch
                )

                return truthy_labels + falsey_labels

            case _:
                raise LoweringError(
                    "Encounted unexpected statement during lowering.",
                    statement.location,
                )
