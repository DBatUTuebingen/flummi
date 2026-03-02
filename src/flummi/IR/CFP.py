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
    "Assignment",
    "Emit",
    "Where",
    "Merge",
)


Label = common.Identifier


@dataclass
class Graph(common.Located):
    primitives: dict[Label, Primitive]
    transitions: graph.Graph[Label]


@dataclass
class Primitive(common.Located, ABC): ...


@dataclass
class Start(Primitive): ...


@dataclass
class Assignment(Primitive):
    variable: common.Identifier
    expression: common.Expression


@dataclass
class Emit(Primitive):
    variable: common.Identifier


@dataclass
class Where(Primitive):
    condition: common.Identifier
    inverted: bool


@dataclass
class Merge(Primitive): ...


Program = common.Program[Graph]
