from abc import ABC
from dataclasses import dataclass

from .common import (
    Variable,
    Label,
    Expression,
    Type,
    Located,
    Program as BaseProgram,
)

__all__ = (
    "Program",
    "Statement",
    "Block",
    "Assignment",
    "Stop",
    "Emit",
    "NoOp",
    "Conditional",
    "Declaration",
    "Loop",
    "Continue",
    "Break",
    "Label",
    "Variable",
    "Expression",
    "Type",
)


class Statement(Located, ABC): ...


@dataclass
class Declaration(Statement):
    variable: Variable
    type: Type


@dataclass
class Block(Statement):
    statements: list[Statement]


@dataclass
class Assignment(Statement):
    variable: Variable
    expression: Expression


@dataclass
class Emit(Statement):
    variable: Variable


@dataclass
class Stop(Statement): ...


@dataclass
class NoOp(Statement): ...


@dataclass
class Conditional(Statement):
    condition: Variable
    true_branch: Statement
    false_branch: Statement


@dataclass
class Loop(Statement):
    label: Label
    body: Statement


@dataclass
class Continue(Statement):
    label: Label


@dataclass
class Break(Statement):
    label: Label


Program = BaseProgram[Statement]
