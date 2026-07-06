from abc import ABC
from dataclasses import dataclass

from ..library import graph
from .common import Expression, Label, Located, Variable
from .common import Program as BaseProgram

__all__ = (
    "Assignment",
    "Emit",
    "Expression",
    "Fork",
    "Gather",
    "Jump",
    "IsSynced",
    "Label",
    "Label",
    "Merge",
    "Plan",
    "Primitive",
    "Program",
    "Start",
    "Stop",
    "Variable",
    "Where",
)


@dataclass
class Plan(Located):
    entry_label: Label
    primitives: dict[Label, Primitive]
    successors_of: graph.Graph[Label]
    virtual_successors_of: graph.Graph[Label]


@dataclass
class Primitive(Located, ABC): ...


@dataclass
class Start(Primitive): ...


@dataclass
class Stop(Primitive): ...


@dataclass
class Assignment(Primitive):
    bindings: dict[Variable, Expression]


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
class Jump(Primitive):
    label: Label


@dataclass
class Fork(Primitive):
    variables: list[Variable]
    expression: Expression


@dataclass
class Gather(Primitive):
    aggregates: dict[Variable, Expression]
    keys: set[Variable]


@dataclass
class IsSynced(Primitive):
    variable: Variable
    label: Label
    keys: set[Variable]


Program = BaseProgram[Plan]
