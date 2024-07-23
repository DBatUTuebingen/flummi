from __future__ import annotations
from abc import ABC
from dataclasses import dataclass

from . import common, AST
from ..library import graph


__all__ = (
    "Function",
    "Program",
    "Label",
    "Graph",
)


type Program[A] = common.Program[A, Graph[A]]
type Function[A] = common.Function[A, Graph[A]]
type Label[A] = common.Identifier[A]


@dataclass
class Graph[A](common.Annotated[A]):
    entry_label: Label[A]
    nodes: dict[Label[A], Node[A]]
    edges: graph.Graph[Label[A]]


@dataclass
class Node[A](common.Annotated[A], ABC):
    ...


@dataclass
class Conditional[A](Node[A]):
    truthy: list[common.Identifier[A]]
    falsey: list[common.Identifier[A]]


@dataclass
class Merge[A](Node[A]):
    ...


@dataclass
class Assignments[A](Node[A]):
    assignments: list[AST.Assignment[A]]


@dataclass
class Emits[A](Node[A]):
    emits: list[AST.Emit[A]]


@dataclass
class Source[A](Node[A]):
    label: common.Identifier[A]


@dataclass
class Sink[A](Node[A]):
    label: common.Identifier[A]


@dataclass
class Fork[A](Node[A]):
    variables: list[common.Identifier[A]]
    expression: common.Expression[A]


@dataclass
class Join[A](Node[A]):
    variables: list[common.Identifier[A]]
    expression: common.Expression[A]


@dataclass
class Mark[A](Node[A]):
    ...


@dataclass
class Wait[A](Node[A]):
    ...
