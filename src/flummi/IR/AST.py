from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from . import common

__all__ = (
    "Program",
    "Statement",
    "Block",
    "Assignment",
    "Stop",
    "Emit",
    "NoOp",
    "Conditional",
)


class Statement(common.Located, ABC): ...


@dataclass
class Block(Statement):
    statements: list[Statement]


@dataclass
class Assignment(Statement):
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
class Conditional(Statement):
    condition: common.Identifier
    true_branch: Statement
    false_branch: Statement


Program = common.Program[Statement]
