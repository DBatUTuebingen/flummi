from __future__ import annotations
from abc import ABC
from dataclasses import dataclass

from . import common


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
    edges: dict[Label, list[Label]]


@dataclass
class Node[A](common.Annotated[A], ABC):
    ...


@dataclass
class Conditional[A](Node[A]):
    truthy: list[common.Identifier[A]]
    falsey: list[common.Identifier[A]]


@dataclass
class Assignment[A](Node[A]):
    variables: list[common.Identifier[A]]
    expression: common.Expression[A]


@dataclass
class Emit[A](Node[A]):
    variables: list[common.Identifier[A]]
