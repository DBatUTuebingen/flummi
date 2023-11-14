from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

from . import common


__all__ = (
    "Program",
    "Function",
    "Statement",
    "Loop",
    "Continue",
    "Break",
    "If",
    "Emit",
    "Stop",
    "Declaration",
    "Assignment",
    "Block",
)


E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


@dataclass
class Program(Generic[E, T]):
    inputs: list[common.Expression[E]]
    function: Function[E, T]


@dataclass
class Function(Generic[E, T]):
    parameters: dict[common.Variable, common.Type[T]]
    emits: common.Type[T]
    body: Statement[E, T]



class Statement(Generic[E, T], ABC):
    ...


@dataclass
class Loop(Statement[E, T]):
    name: str
    body: Statement[E, T]


@dataclass
class Continue(Statement[E, T]):
    name: str


@dataclass
class Break(Statement[E, T]):
    name: str


@dataclass
class If(Statement[E, T]):
    condition: common.Expression[E]
    truthy_branch: Statement[E, T]
    falsey_branch: Statement[E, T]


@dataclass
class Emit(Statement[E, T]):
    to_emit: common.Expression[E]


@dataclass
class Stop(Statement[E, T]):
    ...


@dataclass
class Declaration(Statement[E, T]):
    variable: common.Variable
    type: common.Type[T]


@dataclass
class Assignment(Statement[E, T]):
    variable: common.Variable
    expression: common.Expression[E]


@dataclass
class Block(Statement[E, T]):
    statements: list[Statement[E, T]]
