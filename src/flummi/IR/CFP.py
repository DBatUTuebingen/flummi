from abc import ABC
from dataclasses import dataclass

from . import common
from ..library import graph


__all__ = (
    "Program",
    "Label",
    "Graph",
    "Primitive",
    "Start",
    "Let",
    "Emit",
    "Merge",
    "Where",
    "WhereNot",
    "Fork",
    "Gather",
    "SiblingProbe",
)


Label = common.Identifier
type PerLabel[T] = dict[Label, T]

Variable = common.Identifier


@dataclass(slots=True)
class Primitive(common.Located, ABC): ...


@dataclass(slots=True)
class Start(Primitive): ...


@dataclass(slots=True)
class Let(Primitive):
    variable: Variable
    expression: common.Expression


@dataclass(slots=True)
class Emit(Primitive):
    variable: Variable


@dataclass(slots=True)
class Merge(Primitive): ...


@dataclass(slots=True)
class Where(Primitive):
    condition: Variable


@dataclass(slots=True)
class WhereNot(Primitive):
    condition: Variable


@dataclass(slots=True)
class GoTo(Primitive):
    label: Label


@dataclass(slots=True)
class Fork(Primitive):
    variables: list[Variable]
    expression: common.Expression


@dataclass(slots=True)
class Gather(Primitive):
    aggregates: dict[Variable, common.Expression]
    keys: list[Variable]


@dataclass(slots=True)
class SiblingProbe(Primitive):
    variable: Variable
    label: Label


@dataclass(slots=True)
class Graph(common.Located):
    primitives: PerLabel[Primitive]
    entry_label: Label
    direct_edges: graph.Graph[Label]
    indirect_edges: graph.Graph[Label]


Program = common.Program[Graph]
