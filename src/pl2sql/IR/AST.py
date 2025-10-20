from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from . import common

__all__ = (
    "Program",
    "Statement",
    "Block",
    "Declare",
    "Let",
    "Stop",
    "Emit",
    "NoOp",
    "If",
)


class Statement(common.Located, ABC): ...


@dataclass
class Block(Statement):
    statements: list[Statement]


@dataclass
class Declare(Statement):
    variable: common.Identifier
    type: common.Type


@dataclass
class Let(Statement):
    variable: common.Identifier
    expression: common.Expression


@dataclass
class Emit(Statement):
    variable: common.Identifier


@dataclass
class Stop(Statement): ...


@dataclass
class NoOp(Statement): ...


@dataclass
class If(Statement):
    condition: common.Identifier
    truthy_branch: Statement
    falsey_branch: Statement


Program = common.Program[Statement]
