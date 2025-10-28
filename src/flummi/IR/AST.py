from abc import ABC
from dataclasses import dataclass

from . import common

__all__ = (
    "Program",
    "Statement",
    "Variable",
    "LoopName",
    "Block",
    "Declare",
    "Let",
    "Stop",
    "Emit",
    "NoOp",
    "If",
    "Loop",
    "Continue",
    "Break",
)

Variable = common.Identifier
LoopName = common.Identifier


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


@dataclass(slots=True)
class Loop(Statement):
    name: LoopName
    body: Statement


@dataclass(slots=True)
class Continue(Statement):
    name: LoopName


@dataclass(slots=True)
class Break(Statement):
    name: LoopName


@dataclass(slots=True)
class Fork(Statement):
    variables: list[Variable]
    expression: common.Expression


@dataclass(slots=True)
class Gather(Statement):
    aggregates: dict[Variable, common.Expression]
    keys: list[Variable]


@dataclass(slots=True)
class Sync(Statement): ...


Program = common.Program[Statement]
