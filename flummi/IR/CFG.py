from __future__ import annotations
from abc import ABC
from dataclasses import dataclass

from . import common
from ..library import graph


__all__ = (
    "Function",
    "Program",
    "Label",
    "Graph",
    "Let",
    "Emit",
    "Where",
    "WhereNot",
    "Merge",
    "Push",
    "Pop",
    "Link",
    "Resume",
    "Lookup",
    "Memoize",
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
class Let[A](Node[A]):
    variable: common.Identifier[A]
    expression: common.Expression[A]


@dataclass
class Emit[A](Node[A]):
    function: common.Identifier[A]
    variable: common.Identifier[A]


@dataclass
class Where[A](Node[A]):
    variable: common.Identifier[A]


@dataclass
class WhereNot[A](Node[A]):
    variable: common.Identifier[A]


@dataclass
class Merge[A](Node[A]):
    ...


@dataclass
class Push[A](Node[A]):
    label: common.Identifier[A]


@dataclass
class Pop[A](Node[A]):
    label: common.Identifier[A]


@dataclass
class Link[A](Node[A]):
    label: common.Identifier[A]


@dataclass
class Resume[A](Node[A]):
    function: common.Identifier[A]
    variable: common.Identifier[A]


@dataclass
class Lookup[A](Node[A]):
    result: common.Identifier[A]
    hit: common.Identifier[A]
    function: common.Identifier[A]
    arguments: dict[common.Identifier[A], common.Identifier[A]]


@dataclass
class Memoize[A](Node[A]):
    function: common.Identifier[A]
    arguments: dict[common.Identifier[A], common.Identifier[A]]
    value: common.Identifier[A]
