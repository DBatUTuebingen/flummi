from __future__ import annotations
from abc import ABC
from dataclasses import dataclass

from . import common

__all__ = (
    "Program",
    "Function",
    "Statement",
    "If",
    "Loop",
    "Break",
    "Continue",
    "Declaration",
    "Let",
    "Stop",
    "Emit",
    "NoOp",
    "TailCall",
    "Call",
    "Lookup",
    "Memoize",
)


type Program[A] = common.Program[A, Statement[A]]
type Function[A] = common.Function[A, Statement[A]]


class Statement[A](common.Annotated[A], ABC):
    ...


@dataclass
class Loop[A](Statement[A]):
    name: common.Identifier[A]
    body: Statement[A]


@dataclass
class Continue[A](Statement[A]):
    name: common.Identifier[A]


@dataclass
class Break[A](Statement[A]):
    name: common.Identifier[A]

@dataclass
class Stop[A](Statement[A]):
    ...


@dataclass
class Emit[A](Statement[A]):
    variable: common.Identifier[A]


@dataclass
class Declaration[A](Statement[A]):
    variables: list[common.Identifier[A]]
    type: common.Type[A]


@dataclass
class Let[A](Statement[A]):
    variable: common.Identifier[A]
    expression: common.Expression[A]


@dataclass
class TailCall[A](Statement[A]):
    function: common.Identifier[A]
    arguments: dict[common.Identifier[A], common.Identifier[A]]


@dataclass
class Call[A](TailCall[A]):
    variable: common.Identifier[A]


@dataclass
class Block[A](Statement[A]):
    statements: list[Statement]


@dataclass
class NoOp[A](Statement[A]):
    ...


@dataclass
class If[A](Statement[A]):
    condition: common.Identifier[A]
    truthy_branch: Statement[A]
    falsey_branch: Statement[A]


@dataclass
class Lookup[A](Statement[A]):
    result: common.Identifier[A]
    hit: common.Identifier[A]
    function: common.Identifier[A]
    arguments: dict[common.Identifier[A], common.Identifier[A]]


@dataclass
class Memoize[A](Statement[A]):
    function: common.Identifier[A]
    arguments: dict[common.Identifier[A], common.Identifier[A]]
    value: common.Identifier[A]
