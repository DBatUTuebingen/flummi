from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from . import common
from ..library import graph


__all__ = (
    "Program",
    "Label",
    "Graph",
    "Start",
    "Let",
    "Emit",
)


Label = common.Identifier


@dataclass
class Graph(common.Located):
    entry_label: Label
    nodes: dict[Label, Node]
    edges: graph.Graph[Label]


@dataclass
class Node(common.Located, ABC): ...


@dataclass
class Start(Node): ...


@dataclass
class Let(Node):
    variable: common.Identifier
    expression: common.Expression


@dataclass
class Emit(Node):
    variable: common.Identifier


Program = common.Program[Graph]
