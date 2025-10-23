from __future__ import annotations

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
)


Label = common.Identifier


@dataclass
class Graph(common.Located):
    primitives: dict[Label, Primitive]
    transitions: graph.Graph[Label]
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


Program = common.Program[Graph]
