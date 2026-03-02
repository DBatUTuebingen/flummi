from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto, unique

from flummi.library.utils import union

from ..IR import common, AST, CFP

from ..library import errors


__all__ = ("lower",)


def lower(program: AST.Program) -> CFP.Program:
    return Lowering().lower_program(program)


class LoweringError(errors.PrettyError, ValueError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


@unique
class MultiplexBehavior(Enum):
    MERGE = auto()
    FAN = auto()


MULTIPLEX_DEFAULT = MultiplexBehavior.MERGE
MULTIPLEX_CONFIG: dict[type[AST.Statement], MultiplexBehavior] = {
    AST.Stop: MultiplexBehavior.FAN,
    AST.Emit: MultiplexBehavior.FAN,
    AST.Block: MultiplexBehavior.FAN,
    AST.NoOp: MultiplexBehavior.FAN,
}


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
            predecessors=set(),
            name="start",
        )

        _ = self.lower_statement({entry_label}, program.body)

        graph = CFP.Graph(
            primitives=self._primitives,
            transitions=self._edges,
            location=program.location,
        )

        return CFP.Program(body=graph, location=program.location)

    def add_primitive(
        self,
        primitive: CFP.Primitive,
        predecessors: set[CFP.Label],
        name: str | None = None,
    ) -> CFP.Label:
        label = self._make_label(
            name or type(primitive).__name__.lower(),
            location=primitive.location,
        )
        self._primitives[label] = primitive
        self._edges[label] = set()
        for predecessor in predecessors:
            self._edges[predecessor].add(label)
        return label

    def lower_statement(
        self, predecessors: set[CFP.Label], statement: AST.Statement
    ) -> set[CFP.Label]:
        match len(predecessors):
            case 0:
                return set()

            case 1:
                match statement:
                    case AST.Assignment(variable, expression):
                        this_label = self.add_primitive(
                            predecessors=predecessors,
                            primitive=CFP.Assignment(
                                variable=variable,
                                expression=expression,
                                location=statement.location,
                            ),
                        )

                        return {this_label}

                    case AST.Stop():
                        return set()

                    case AST.Emit(variable):
                        this_label = self.add_primitive(
                            predecessors=predecessors,
                            primitive=CFP.Emit(
                                variable=variable,
                                location=statement.location,
                            ),
                        )

                        return predecessors

                    case AST.Block(statements):
                        for statement in statements:
                            if predecessors:
                                predecessors = self.lower_statement(
                                    predecessors, statement
                                )

                        return predecessors

                    case AST.Conditional(condition, true_branch, false_branch):
                        where = self.add_primitive(
                            predecessors=predecessors,
                            primitive=CFP.Where(
                                condition,
                                inverted=False,
                                location=statement.location,
                            ),
                        )
                        where_not = self.add_primitive(
                            predecessors=predecessors,
                            primitive=CFP.Where(
                                condition,
                                inverted=True,
                                location=statement.location,
                            ),
                        )

                        return self.lower_statement(
                            {where},
                            true_branch,
                        ) | self.lower_statement(
                            {where_not},
                            false_branch,
                        )

                    case _:
                        raise LoweringError(
                            "Encounted unexpected statement during lowering.",
                            statement.location,
                        )

            case _:
                match MULTIPLEX_CONFIG.get(type(statement), MULTIPLEX_DEFAULT):
                    case MultiplexBehavior.FAN:
                        return union(
                            self.lower_statement({predecessor}, statement)
                            for predecessor in predecessors
                        )

                    case MultiplexBehavior.MERGE:
                        merge = self.add_primitive(
                            predecessors=predecessors,
                            primitive=CFP.Merge(location=statement.location),
                        )
                        return self.lower_statement({merge}, statement)
