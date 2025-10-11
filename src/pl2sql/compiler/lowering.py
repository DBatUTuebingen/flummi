from collections import defaultdict
from dataclasses import dataclass, field

from ..IR import common, AST, CFP

from ..library import errors


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

    def lower_program(self, program: AST.Program) -> CFP.Program:
        entry_label = self.add_primitive(
            primitive=CFP.Start(
                location=program.location,
            ),
            name="start",
        )

        _ = self.lower_statement(entry_label, program.body)

        graph = CFP.Graph(
            primitives=self._primitives,
            transitions=self._edges,
            location=program.location,
        )

        return CFP.Program(body=graph, location=program.location)

    def add_primitive(
        self,
        primitive: CFP.Primitive,
        predecessor: CFP.Label | None = None,
        name: str | None = None,
    ) -> CFP.Label:
        label = self._make_label(
            name or type(primitive).__name__.lower(),
            location=primitive.location,
        )
        self._primitives[label] = primitive
        self._edges[label] = set()
        if predecessor:
            self._edges[predecessor].add(label)
        return label

    def lower_statement(
        self, predecessor: CFP.Label | None, statement: AST.Statement
    ) -> CFP.Label | None:
        match statement:
            case AST.NoOp():
                return predecessor

            case AST.Let(variable, expression):
                this_label = self.add_primitive(
                    predecessor=predecessor,
                    primitive=CFP.Let(
                        variable=variable,
                        expression=expression,
                        location=statement.location,
                    ),
                )

                return this_label

            case AST.Stop():
                return

            case AST.Emit(variable):
                this_label = self.add_primitive(
                    predecessor=predecessor,
                    primitive=CFP.Emit(
                        variable=variable,
                        location=statement.location,
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
                    statement.location,
                )
