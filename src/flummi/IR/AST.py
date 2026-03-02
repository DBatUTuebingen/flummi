from abc import ABC
from dataclasses import dataclass

from . import common

__all__ = (
    "Variable",
    "Expression",
    "Type",
    "Program",
    "Statement",
    "Block",
    "Assignment",
    "Stop",
    "Emit",
    "NoOp",
    "Conditional",
    "Declaration",
)

Variable = common.Identifier
Expression = common.Expression
Type = common.Type


class Statement(common.Located, ABC): ...


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


Program = common.Program[Statement]
