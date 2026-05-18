from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto, unique

from ..IR import AST, CFP
from ..library import errors
from ..library.utils import union
from .names import SystemVariable

__all__ = ("lower",)


class LoweringError(errors.PrettyError):
    base_exception = ValueError


@dataclass(frozen=True)
class Multiplexing:
    @unique
    class Method(Enum):
        MERGE = auto()
        FAN = auto()

    default: Method = Method.MERGE
    overrides: dict[type[AST.Statement], Method] = field(
        default_factory=lambda: {
            AST.Assignment: Multiplexing.Method.MERGE,
            AST.Block: Multiplexing.Method.MERGE,
            AST.Break: Multiplexing.Method.FAN,
            AST.Continue: Multiplexing.Method.FAN,
            AST.Declaration: Multiplexing.Method.FAN,
            AST.Emit: Multiplexing.Method.FAN,
            AST.Fork: Multiplexing.Method.MERGE,
            AST.Gather: Multiplexing.Method.MERGE,
            AST.Loop: Multiplexing.Method.MERGE,
            AST.NoOp: Multiplexing.Method.FAN,
            AST.Stop: Multiplexing.Method.FAN,
            AST.Sync: Multiplexing.Method.MERGE,
            AST.Stop: Multiplexing.Method.FAN,
        }
    )

    def method_for(self, statement: AST.Statement) -> Method:
        return self.overrides.get(type(statement), self.default)


def lower(
    program: AST.Program,
    multiplexing: Multiplexing = Multiplexing(),
) -> CFP.Program:
    return Lowering(multiplexing).lower_program(program)


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
    _loop_labels: list[CFP.Label] = field(init=False, default_factory=list)
    _loop_exits: list[set[CFP.Label]] = field(init=False, default_factory=list)

    def _make_label(
        self, name: str, location: errors.Location | None
    ) -> CFP.Label:
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
            name="start",
        )

        _ = self.lower_statement({entry_label}, program.body)

        graph = CFP.Plan(
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
        name: str | None = None,
    ) -> CFP.Label:
        label = self._make_label(
            name or type(primitive).__name__.lower(),
            location=primitive.location,
        )
        self._primitives[label] = primitive
        self._edges[label] = set()
        self._virtual_edges[label] = set()
        return label

    def _add_edge(self, source: CFP.Label, sink: CFP.Label):
        self._edges[source].add(sink)

    def _add_virtual_edge(
        self,
        source: CFP.Label,
        sink: CFP.Label,
        location: errors.Location | None = None,
    ):
        goto_label = self._add_primitive(
            CFP.Jump(sink, location=location or source.location)
        )
        self._add_edge(source, goto_label)
        self._virtual_edges[goto_label].add(sink)

    def lower_statement(
        self, predecessors: set[CFP.Label], statement: AST.Statement
    ) -> set[CFP.Label]:
        match statement:
            case AST.NoOp() | AST.Declaration() | AST.Block([]):
                return predecessors

            case _ if len(predecessors) == 0:
                return set()

            case _ if len(predecessors) == 1:
                predecessor = list(predecessors)[0]

                match statement:
                    case AST.Stop():
                        this_label = self._add_primitive(
                            primitive=CFP.Stop(location=statement.location)
                        )

                        self._add_edge(predecessor, this_label)

                        return set()

                    case AST.Assignment(probe_variable, expression):
                        this_label = self._add_primitive(
                            primitive=CFP.Assignment(
                                variable=probe_variable,
                                expression=expression,
                                location=statement.location,
                            ),
                        )

                        self._add_edge(predecessor, this_label)

                        return {this_label}

                    case AST.Emit(probe_variable):
                        this_label = self._add_primitive(
                            primitive=CFP.Emit(
                                variable=probe_variable,
                                location=statement.location,
                            ),
                        )

                        self._add_edge(predecessor, this_label)

                        return {this_label}

                    case AST.Block(statements):
                        for statement in statements:
                            if predecessors:
                                predecessors = self.lower_statement(
                                    predecessors, statement
                                )

                        return predecessors

                    case AST.Conditional(condition, true_branch, false_branch):
                        where = self._add_primitive(
                            primitive=CFP.Where(
                                condition,
                                inverted=False,
                                location=statement.location,
                            ),
                        )
                        where_not = self._add_primitive(
                            primitive=CFP.Where(
                                condition,
                                inverted=True,
                                location=statement.location,
                            ),
                        )

                        self._add_edge(predecessor, where)
                        self._add_edge(predecessor, where_not)

                        return self.lower_statement(
                            {where},
                            true_branch,
                        ) | self.lower_statement(
                            {where_not},
                            false_branch,
                        )

                    case AST.Loop(body):
                        loop_head = self._add_primitive(
                            primitive=CFP.Start(location=statement.location),
                        )

                        self._loop_labels.append(loop_head)
                        self._loop_exits.append(set())

                        loop_tails = self.lower_statement(
                            {loop_head, predecessor}, body
                        )

                        _ = self.lower_statement(
                            loop_tails,
                            AST.Continue(location=statement.location),
                        )

                        del self._loop_labels[-1]
                        return self._loop_exits.pop()

                    case AST.Continue():
                        self._add_virtual_edge(
                            predecessor,
                            self._loop_labels[-1],
                            location=statement.location,
                        )

                        return set()

                    case AST.Break():
                        self._loop_exits[-1].add(predecessor)
                        return set()

                    case AST.Fork(variables, expression):
                        this_label = self._add_primitive(
                            primitive=CFP.Fork(
                                variables=variables,
                                expression=expression,
                                location=statement.location,
                            ),
                        )

                        self._add_edge(predecessor, this_label)

                        return {this_label}

                    case AST.Gather(aggregates, keys):
                        this_label = self._add_primitive(
                            primitive=CFP.Gather(
                                aggregates=aggregates,
                                keys=keys,
                                location=statement.location,
                            ),
                        )

                        self._add_edge(predecessor, this_label)

                        return {this_label}

                    case AST.Sync(keys):
                        probe_variable: CFP.Variable = self._make_label(
                            SystemVariable.PROBE, statement.location
                        )

                        start = self._add_primitive(
                            primitive=CFP.Start(
                                location=statement.location,
                            ),
                        )
                        probe = self._add_primitive(
                            primitive=CFP.IsSynced(
                                variable=probe_variable,
                                label=start,
                                keys=keys,
                                location=statement.location,
                            ),
                        )
                        probe_success = self._add_primitive(
                            primitive=CFP.Where(
                                condition=probe_variable,
                                inverted=False,
                                location=statement.location,
                            )
                        )
                        probe_failure = self._add_primitive(
                            primitive=CFP.Where(
                                condition=probe_variable,
                                inverted=True,
                                location=statement.location,
                            )
                        )

                        self._add_virtual_edge(predecessor, start)
                        self._add_edge(start, probe)
                        self._add_edge(probe, probe_success)
                        self._add_edge(probe, probe_failure)
                        self._add_virtual_edge(probe_failure, start)

                        return {probe_success}

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
                            primitive=CFP.Merge(location=statement.location),
                        )
                        for predecessor in predecessors:
                            self._add_edge(predecessor, merge)
                        return self.lower_statement({merge}, statement)
