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
type Label = common.Identifier[None]


@dataclass
class Graph[A](common.Annotated[A]):
    entry_label: Label
    nodes: dict[Label, Node[A]]
    edges: graph.Graph[Label]


@dataclass
class Node[A](ABC):
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
class Aggregate[A](Node[A]):
    aggregates: dict[common.Identifier[A], common.Expression[A]]


@dataclass
class Mark[A](Node[A]):
    ...


@dataclass
class Wait[A](Node[A]):
    ...
