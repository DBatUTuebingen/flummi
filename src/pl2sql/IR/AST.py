from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from . import common

__all__ = (
    "Program",
    "Statement",
    "Block",
    "Let",
    "Stop",
    "Emit",
    "NoOp",
)


type Program[A] = common.Program[A, Statement[A]]


class Statement[A](common.Annotated[A], ABC): ...


@dataclass
class Block[A](Statement[A]):
    statements: list[Statement[A]]


@dataclass
class Let[A](Statement[A]):
    variable: common.Identifier[A]
    expression: common.Expression[A]


@dataclass
class Emit[A](Statement[A]):
    variable: common.Identifier[A]


@dataclass
class Stop[A](Statement[A]): ...


@dataclass
class NoOp[A](Statement[A]): ...
