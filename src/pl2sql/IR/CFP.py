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


type Program[A] = common.Program[A, Graph[A]]
type Label[A] = common.Identifier[A]


@dataclass
class Graph[A](common.Annotated[A]):
    entry_label: Label[A]
    nodes: dict[Label[A], Node[A]]
    edges: graph.Graph[Label[A]]


@dataclass
class Node[A](common.Annotated[A], ABC): ...


@dataclass
class Start[A](Node[A]): ...


@dataclass
class Let[A](Node[A]):
    variable: common.Identifier[A]
    expression: common.Expression[A]


@dataclass
class Emit[A](Node[A]):
    variable: common.Identifier[A]
