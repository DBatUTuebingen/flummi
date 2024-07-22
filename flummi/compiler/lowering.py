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
type Label        = CFG.Label
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

    def _make_label(self, name: str) -> Label:
        self._label_counters[name] += 1
        return common.Identifier(
            f"{name}.{self._label_counters[name]}",
            annotation=None
        )

    def lower_function(self, function: parser.Function) -> Function:
        entry_label = self._make_label("entry")
        self._nodes[entry_label] = CFG.Source(function.name)
        self._edges[entry_label] = set()

        self.lower_statement(
            previous_labels=[entry_label],
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

    def lower_statement(
        self,
        previous_labels: list[Label],
        statement: parser.Statement
    ) -> list[Label]:
        if len(previous_labels) > 1:
            merge_label = self._make_label("merge")
            self._nodes[merge_label] = CFG.Merge()
            self._edges[merge_label] = set()
            for label in previous_labels:
                self._edges[label].add(merge_label)
            previous_label = merge_label
        elif len(previous_labels) == 1:
            previous_label = previous_labels[0]
        else:
            raise LoweringError(
                "Tried to lower statement without any predecessors.",
                statement.annotation
            )

        match statement:
            case AST.NoOp():
                return previous_labels

            case AST.Stop():
                return []

            case AST.Assignment():
                this_label = self._make_label("assignment")
                self._nodes[this_label] = CFG.Assignments([statement])
                self._edges[this_label] = set()
                self._edges[previous_label].add(this_label)
                return [this_label]

            case AST.Emit():
                this_label = self._make_label("emit")
                self._nodes[this_label] = CFG.Emits([statement])
                self._edges[this_label] = set()
                self._edges[previous_label].add(this_label)
                return [previous_label]

            case AST.Block(statements):
                _previous_labels: list[Label] = previous_labels
                for statement in statements:
                    if _previous_labels:
                        _previous_labels = self.lower_statement(
                            _previous_labels,
                            statement
                        )
                return _previous_labels

            case AST.If(condition, truthy_branch, falsey_branch):
                truthy_label = self._make_label("truthy")
                self._nodes[truthy_label] = CFG.Conditional(
                    truthy=[condition],
                    falsey=[]
                )
                self._edges[truthy_label] = set()
                self._edges[previous_label].add(truthy_label)
                final_truthy_label = self.lower_statement(
                    [truthy_label],
                    truthy_branch
                )

                falsey_label = self._make_label("falsey")
                self._nodes[falsey_label] = CFG.Conditional(
                    truthy=[],
                    falsey=[condition]
                )
                self._edges[falsey_label] = set()
                self._edges[previous_label].add(falsey_label)
                final_falsey_label = self.lower_statement(
                    [falsey_label],
                    falsey_branch
                )

                return final_truthy_label + final_falsey_label

            case AST.Loop(name, body):
                loop_label = self._make_label(name.identifier)
                self._nodes[loop_label] = CFG.Source(name)
                self._edges[loop_label] = set()

                loopback_labels = self.lower_statement(
                    previous_labels + [loop_label],
                    body
                )

                if loopback_labels:
                    self.lower_statement(
                        loopback_labels,
                        AST.Continue(
                            name,
                            annotation=statement.annotation
                        )
                    )

                return self._loop_exits[name]

            case AST.Continue(name):
                this_label = self._make_label("sink")
                self._nodes[this_label] = CFG.Sink(name)
                self._edges[this_label] = set()
                self._edges[previous_label].add(this_label)
                return []

            case AST.Break(name):
                self._loop_exits[name].extend(previous_labels)
                return []

            case _:
                raise LoweringError(
                    "Encounted unexpected statement during lowering.",
                    statement.annotation
                )
