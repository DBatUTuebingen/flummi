from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from . import common

__all__ = (
    "Program",
    "Statement",
    "Variable",
    "Block",
    "Declare",
    "Let",
    "Stop",
    "Emit",
    "NoOp",
    "If",
)

Variable = common.Identifier

class Statement(common.Located, ABC): ...


@dataclass
class Block(Statement):
    statements: list[Statement]


@dataclass
class Declare(Statement):
    variable: Variable
    type: common.Type


@dataclass
class Let(Statement):
    variable: Variable
    expression: common.Expression


@dataclass
class Emit(Statement):
    variable: Variable


@dataclass
class Stop(Statement): ...


@dataclass
class NoOp(Statement): ...


@dataclass
class If(Statement):
    condition: Variable
    truthy_branch: Statement
    falsey_branch: Statement


Program = common.Program[Statement]
