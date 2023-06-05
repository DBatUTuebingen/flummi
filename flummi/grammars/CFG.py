from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

from . import common


__all__ = (
    "BlockLabel",
    "Graph",
    "Block",
    "Statement",
    "Emit",
    "Assignment",
    "Terminal",
    "Jump",
    "GoTo",
    "Stop",
    "If",
    "Variable",
    "Predicate",
    "Not",
    "And",
    "Tautology",
    "JumpDirective",
    "Reference",
    "FromLoop",
    "FromBlock",
    "Node"
)


E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


@dataclass
class BlockLabel:
    label: str

    def __hash__(self) -> int:
        return hash(self.label)


@dataclass
class Graph(Generic[E, T]):
    entry_label: BlockLabel
    inputs: dict[common.Variable, common.Expression[E]]
    emits: common.Type[T]
    variables: dict[common.Variable, common.Type[T]]
    blocks: dict[BlockLabel, Block[E]]
    jumps: list[JumpDirective]


@dataclass
class Block(Generic[E]):
    label: BlockLabel
    parameters: list[common.Variable]
    statements: list[Statement[E]]
    terminal: Terminal
    predecessor_references: list[Reference]


class Statement(Generic[E], ABC):
    ...


@dataclass
class Emit(Statement[E]):
    to_emit: common.Expression[E]


@dataclass
class Assignment(Statement[E]):
    variable: common.Variable
    expression: common.Expression[E]


class Terminal(ABC):
    ...


@dataclass
class Jump(Terminal):
    label: BlockLabel
    arguments: list[common.Variable]


@dataclass
class GoTo(Terminal):
    label: BlockLabel
    arguments: list[common.Variable]


@dataclass
class Stop(Terminal):
    ...


@dataclass
class If(Terminal):
    condition: common.Variable
    truthy_terminal: Terminal
    falsey_terminal: Terminal


@dataclass
class JumpDirective:
    origin: BlockLabel
    destination: BlockLabel
    parameters: list[common.Variable]
    predicate: Predicate


class Predicate(ABC):
    ...


@dataclass
class Variable(Predicate):
    variable: common.Variable


@dataclass
class Not(Predicate):
    operand: Predicate


@dataclass
class And(Predicate):
    left_operand: Predicate
    right_operand: Predicate


@dataclass
class Tautology(Predicate):
    ...


class Reference(ABC):
    ...


@dataclass
class FromLoop(Reference):
    expected_label: BlockLabel


@dataclass
class FromBlock(Reference):
    label: BlockLabel
    arguments: list[common.Variable]
    predicate: Predicate


Node = (
    Graph[E, T] |
    Block[E] |
    Statement[E] |
    Terminal |
    JumpDirective |
    Predicate |
    Reference
)
