from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto, unique

from flummi.library.utils import union

from ..IR import AST, CFP

from ..library import errors


__all__ = ("lower",)


def lower(program: AST.Program, multiplexing: Multiplexing) -> CFP.Program:
    return Lowering(multiplexing).lower_program(program)


class LoweringError(errors.PrettyError, ValueError): ...


@dataclass
class Multiplexing:
    @unique
    class Method(Enum):
        MERGE = auto()
        FAN = auto()

    default: Method = Method.MERGE
    overrides: dict[type[AST.Statement], Method] = field(
        default_factory=lambda: {
            AST.Stop: Multiplexing.Method.FAN,
            AST.Emit: Multiplexing.Method.FAN,
            AST.NoOp: Multiplexing.Method.FAN,
            AST.Break: Multiplexing.Method.FAN,
            AST.Continue: Multiplexing.Method.FAN,
        }
    )

    def method_for(self, statement: AST.Statement) -> Method:
        return self.overrides.get(type(statement), self.default)


@dataclass
class Lowering:
    multiplexing: Multiplexing

    _primitives: dict[CFP.Label, CFP.Primitive] = field(
        init=False, default_factory=dict
    )
    _edges: dict[CFP.Label, set[CFP.Label]] = field(
        init=False, default_factory=lambda: defaultdict(set)
    )
    _virtual_edges: dict[CFP.Label, set[CFP.Label]] = field(
        init=False, default_factory=lambda: defaultdict(set)
    )
    _label_counters: dict[str, int] = field(
        init=False, default_factory=lambda: defaultdict(int)
    )
    _loop_labels: dict[AST.Label, CFP.Label] = field(init=False, default_factory=dict)
    _loop_exits: dict[CFP.Label, set[CFP.Label]] = field(
        init=False, default_factory=lambda: defaultdict(set)
    )

    def _make_label(self, name: str, location: errors.Location) -> CFP.Label:
        self._label_counters[name] += 1
        return CFP.Label(
            f"{name}.{self._label_counters[name]}",
            location=location,
        )

    def lower_program(self, program: AST.Program) -> CFP.Program:
        entry_label = self._add_primitive(
            primitive=CFP.Start(
                location=program.location,
            ),
            predecessors=set(),
            name="start",
        )

        _ = self.lower_statement({entry_label}, program.body)

        graph = CFP.Graph(
            entry_label=entry_label,
            primitives=self._primitives,
            successors_of=self._edges,
            virtual_successors_of=self._virtual_edges,
            location=program.location,
        )

        return CFP.Program(body=graph, location=program.location)

    def _add_primitive(
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
        if isinstance(primitive, CFP.GoTo):
            self._virtual_edges[label].add(primitive.label)
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
                        this_label = self._add_primitive(
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

                    case AST.NoOp() | AST.Declaration():
                        return predecessors

                    case AST.Emit(variable):
                        this_label = self._add_primitive(
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
                        where = self._add_primitive(
                            predecessors=predecessors,
                            primitive=CFP.Where(
                                condition,
                                inverted=False,
                                location=statement.location,
                            ),
                        )
                        where_not = self._add_primitive(
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

                    case AST.Loop(label, body):
                        loop_head = self._add_primitive(
                            predecessors=set(),
                            primitive=CFP.Start(location=statement.location),
                        )

                        self._loop_labels[label] = loop_head

                        loop_tails = self.lower_statement(
                            {loop_head} | predecessors, body
                        )

                        _ = self.lower_statement(
                            loop_tails,
                            AST.Continue(label, location=statement.location),
                        )

                        return self._loop_exits[label]

                    case AST.Continue(label):
                        _ = self._add_primitive(
                            predecessors=predecessors,
                            primitive=CFP.GoTo(
                                self._loop_labels[label],
                                location=statement.location,
                            ),
                        )
                        return set()

                    case AST.Break(label):
                        self._loop_exits[label].update(predecessors)
                        return set()

                    case _:
                        raise LoweringError(
                            "Encounted unexpected statement during lowering.",
                            statement.location,
                        )

            case _:
                match self.multiplexing.method_for(statement):
                    case Multiplexing.Method.FAN:
                        return union(
                            self.lower_statement({predecessor}, statement)
                            for predecessor in predecessors
                        )

                    case Multiplexing.Method.MERGE:
                        merge = self._add_primitive(
                            predecessors=predecessors,
                            primitive=CFP.Merge(location=statement.location),
                        )
                        return self.lower_statement({merge}, statement)
