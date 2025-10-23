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


@dataclass
class Primitive(common.Located, ABC): ...


@dataclass
class Start(Primitive): ...


@dataclass
class Let(Primitive):
    variable: Variable
    expression: common.Expression


@dataclass
class Emit(Primitive):
    variable: Variable


class Merge(Primitive): ...


@dataclass
class Where(Primitive):
    condition: Variable


@dataclass
class WhereNot(Primitive):
    condition: Variable


Program = common.Program[Graph]
