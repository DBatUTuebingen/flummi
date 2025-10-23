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


@dataclass(slots=True)
class Block(Statement):
    statements: list[Statement]


@dataclass(slots=True)
class Declare(Statement):
    variable: Variable
    type: common.Type


@dataclass(slots=True)
class Let(Statement):
    variable: Variable
    expression: common.Expression


@dataclass(slots=True)
class Emit(Statement):
    variable: Variable


@dataclass(slots=True)
class Stop(Statement): ...


@dataclass(slots=True)
class NoOp(Statement): ...


@dataclass(slots=True)
class If(Statement):
    condition: Variable
    truthy_branch: Statement
    falsey_branch: Statement


Program = common.Program[Statement]
