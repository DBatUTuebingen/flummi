from abc import ABC
from dataclasses import dataclass

from ..library import graph
from .common import Expression, Label, Located, Variable
from .common import Program as BaseProgram

__all__ = (
    "Assignment",
    "Emit",
    "Expression",
    "GoTo",
    "Graph",
    "Label",
    "Label",
    "Merge",
    "Primitive",
    "Program",
    "Start",
    "Variable",
    "Where",
)


@dataclass
class Graph(Located):
    entry_label: Label
    primitives: dict[Label, Primitive]
    successors_of: graph.Graph[Label]
    virtual_successors_of: graph.Graph[Label]


@dataclass
class Primitive(Located, ABC): ...


@dataclass
class Start(Primitive): ...


@dataclass
class Assignment(Primitive):
    variable: Variable
    expression: Expression


@dataclass
class Emit(Primitive):
    variable: Variable


@dataclass
class Where(Primitive):
    condition: Variable
    inverted: bool


@dataclass
class Merge(Primitive): ...


@dataclass
class GoTo(Primitive):
    label: Label


Program = BaseProgram[Graph]
