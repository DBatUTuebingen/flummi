from collections import defaultdict
from dataclasses import dataclass, field

from ..IR import common, AST, CFP
from ..library import errors, graph


__all__ = ("lower",)


def lower(program: AST.Program) -> CFP.Program:
    return Lowering().lower_program(program)


class LoweringError(errors.PrettyError, ValueError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


@dataclass(slots=True)
class Lowering:
    _primitives: dict[CFP.Label, CFP.Primitive] = field(
        init=False, default_factory=dict
    )
    _edges: dict[CFP.Label, set[CFP.Label]] = field(
        init=False, default_factory=lambda: defaultdict(set)
    )
    _backedges: dict[CFP.Label, set[CFP.Label]] = field(
        init=False, default_factory=lambda: defaultdict(set)
    )
    _label_counters: dict[str, int] = field(
        init=False, default_factory=lambda: defaultdict(int)
    )
    _loop_heads: dict[AST.LoopName, CFP.Label] = field(
        init=False, default_factory=dict
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
        self, predecessors: set[CFP.Label], location: errors.Location
    ) -> CFP.Label:
        if len(predecessors) > 1:
            label = self.add_primitive(CFP.Merge(location=location))
            for predecessor in predecessors:
                self.add_edge(predecessor, label)
            return label
        elif len(predecessors) == 1:
            return list(predecessors)[0]
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

        _ = self.lower_statement({entry_label}, program.body)

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
            entry_label=entry_label,
            edges=self._edges,
            backedges=self._backedges,
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

    def add_backedge(
        self,
        source: CFP.Label,
        sink: CFP.Label,
        location: errors.Location | None = None,
    ):
        goto_label = self.add_primitive(
            CFP.GoTo(sink, location=location or source.location)
        )
        self._edges[source].add(goto_label)
        self._backedges[goto_label].add(sink)

    @dataclass(slots=True)
    class StatementResult:
        outgoing_labels: set[CFP.Label] = field(default_factory=set)
        loop_exits: dict[AST.LoopName, set[CFP.Label]] = field(
            default_factory=dict
        )

        def merge(self, other: Lowering.StatementResult):
            self.outgoing_labels |= other.outgoing_labels
            return self.merge_loop_exits(other)

        def merge_loop_exits(self, other: Lowering.StatementResult):
            for name, exits in other.loop_exits.items():
                if name not in self.loop_exits:
                    self.loop_exits[name] = exits
                else:
                    self.loop_exits[name] |= exits
            return self

        def exit_loop(self, name: AST.LoopName):
            self.outgoing_labels = self.loop_exits.pop(name, set())
            return self

    def lower_statement(
        self, predecessors: set[CFP.Label], statement: AST.Statement
    ) -> StatementResult:
        match statement:
            case AST.NoOp():
                return self.StatementResult(predecessors)

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

                return self.StatementResult({this_label})

            case AST.Stop():
                return self.StatementResult()

            case AST.Emit(variable):
                for predecessor in predecessors:
                    emit_label = self.add_primitive(
                        primitive=CFP.Emit(
                            variable=variable,
                            location=statement.location,
                        ),
                    )

                    self.add_edge(predecessor, emit_label)

                return self.StatementResult(predecessors)

            case AST.Block(statements):
                result = self.StatementResult(predecessors)

                for child in statements:
                    if not result.outgoing_labels:
                        break

                    child_result = self.lower_statement(
                        result.outgoing_labels, child
                    )
                    result = child_result.merge_loop_exits(result)

                return result

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

                truthy_result = self.lower_statement(
                    {where_label}, truthy_branch
                )
                falsey_result = self.lower_statement(
                    {where_not_label}, falsey_branch
                )

                return truthy_result.merge(falsey_result)

            case AST.Loop(name, body):
                head_label = self.add_primitive(
                    CFP.Start(location=statement.location)
                )
                self._loop_heads[name] = head_label

                result = self.lower_statement(predecessors | {head_label}, body)

                for loopback_label in result.outgoing_labels:
                    self.add_backedge(
                        loopback_label, head_label, location=statement.location
                    )

                return result.exit_loop(name)

            case AST.Continue(name):
                head_label = self._loop_heads[name]

                for predecessor in predecessors:
                    self.add_backedge(
                        predecessor, head_label, location=statement.location
                    )

                return self.StatementResult()

            case AST.Break(name):
                return self.StatementResult(loop_exits={name: predecessors})

            case _:
                raise LoweringError(
                    "Encounted unexpected statement during lowering.",
                    statement.location,
                )
