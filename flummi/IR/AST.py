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
    "Assignment",
    "Emit",
    "NoOp",
    "Stop",
    "Fork",
    "Join",
    "Sync",
    "Call",
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
class Emit[A](Statement[A]):
    variables: list[common.Identifier[A]]


@dataclass
class Declaration[A](Statement[A]):
    variables: list[common.Identifier[A]]
    type: common.Type[A]


@dataclass
class Assignment[A](Statement[A]):
    variables: list[common.Identifier[A]]
    expression: common.Expression[A]


@dataclass
class Fork[A](Statement[A]):
    variables: list[common.Identifier[A]]
    expression: common.Expression[A]


@dataclass
class Join[A](Statement[A]):
    variables: list[common.Identifier[A]]
    expression: common.Expression[A]


@dataclass
class Call[A](Statement[A]):
    variables: list[common.Identifier[A]]
    function: common.Identifier[A]
    arguments: list[common.Identifier[A]]


@dataclass
class Block[A](Statement[A]):
    statements: list[Statement]


class Sync[A](Statement[A]):
    ...


@dataclass
class Stop[A](Statement[A]):
    ...


@dataclass
class NoOp[A](Statement[A]):
    ...


@dataclass
class If[A](Statement[A]):
    condition: common.Identifier[A]
    truthy_branch: Statement[A]
    falsey_branch: Statement[A]
