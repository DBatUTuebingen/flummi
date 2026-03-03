from abc import ABC
from dataclasses import dataclass

from .common import Located, Label, Variable, Expression, Program as BaseProgram
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
    "GoTo",
    "Label",
    "Variable",
    "Expression",
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
