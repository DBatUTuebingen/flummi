from abc import ABC
from dataclasses import dataclass

from .common import (
    Expression,
    Located,
    Type,
    Variable,
)
from .common import (
    Program as BaseProgram,
)

__all__ = (
    "Assignment",
    "Block",
    "Break",
    "Conditional",
    "Continue",
    "Declaration",
    "Emit",
    "Expression",
    "Fork",
    "Gather",
    "Loop",
    "NoOp",
    "Program",
    "Statement",
    "Stop",
    "Sync",
    "Type",
    "Variable",
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
    body: Statement


@dataclass
class Continue(Statement): ...


@dataclass
class Break(Statement): ...


@dataclass
class Fork(Statement):
    variables: list[Variable]
    expression: Expression


@dataclass
class Gather(Statement):
    aggregates: dict[Variable, Expression]
    keys: set[Variable]


@dataclass
class Sync(Statement):
    keys: set[Variable]


Program = BaseProgram[Statement]
