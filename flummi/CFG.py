from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from functools import reduce

from . import grammar

__all__ = (
    "BlockLabel",
    "Graph",
    "Block",
    "Terminal",
    "Jump",
    "GoTo",
    "Stop",
    "If",
)


@dataclass
class BlockLabel:
    label: str

    def __hash__(self) -> int:
        return hash(self.label)


@dataclass
class Graph:
    entry_label: BlockLabel
    blocks: dict[BlockLabel, Block]


@dataclass
class Block:
    label: BlockLabel
    statements: list[Statement]
    terminal: Terminal


class Statement(ABC):
    ...


@dataclass
class Emit(Statement):
    to_emit: grammar.Expression


@dataclass
class Assignment(Statement):
    variable: grammar.Variable
    expression: grammar.Expression


class Terminal(ABC):
    ...


@dataclass
class Jump(Terminal):
    label: BlockLabel


@dataclass
class GoTo(Terminal):
    label: BlockLabel


@dataclass
class Stop(Terminal):
    ...


@dataclass
class If(Terminal):
    condition: grammar.Variable
    truthy_terminal: Terminal
    falsey_terminal: Terminal


type Node = Graph | Block | Statement | Terminal


def successors(block: Block) -> set[BlockLabel]:
    def scan_terminal(terminal: Terminal) -> set[BlockLabel]:
        match terminal:
            case GoTo(label) | Jump(label):
                return {label}
            case If(_, truthy, falsey):
                return scan_terminal(truthy) | scan_terminal(falsey)
            case _:
                return set()

    return scan_terminal(block.terminal)


def jumps(block: Block) -> set[BlockLabel]:
    def scan_terminal(terminal: Terminal) -> set[BlockLabel]:
        match terminal:
            case Jump(label):
                return {label}
            case If(_, truthy, falsey):
                return scan_terminal(truthy) | scan_terminal(falsey)
            case _:
                return set()

    return scan_terminal(block.terminal)


def gotos(block: Block) -> set[BlockLabel]:
    def scan_terminal(terminal: Terminal) -> set[BlockLabel]:
        match terminal:
            case GoTo(label):
                return {label}
            case If(_, truthy, falsey):
                return scan_terminal(truthy) | scan_terminal(falsey)
            case _:
                return set()

    return scan_terminal(block.terminal)


def contains_jumps(block: Block) -> bool:
    return bool(jumps(block))


def contains_emits(block: Block) -> bool:
    return any(
        isinstance(statement, Emit)
        for statement in block.statements
    )


def free_variables(block: Block) -> set[grammar.Variable]:
    vars = set()

    for statement in block.statements:
        match statement:
            case Emit(expression) | Assignment(_, expression):
                vars.update(expression.free_variables)

    vars |= condition_variables(block.terminal) - bound_variables(block)

    return vars


def condition_variables(terminal: Terminal) -> set[grammar.Variable]:
    match terminal:
        case If(var, truthy, falsey):
            return {var} | condition_variables(truthy) | condition_variables(falsey)
        case _:
            return set()



def bound_variables(block: Block) -> set[grammar.Variable]:
    vars = set()

    for statement in block.statements:
        match statement:
            case Assignment(variable, _):
                vars.add(variable)

    return vars


def jumpify(terminal: Terminal, label: BlockLabel) -> Terminal:
    match terminal:
        case GoTo(_label) if _label == label:
            return Jump(label)
        case If(condition, truthy, falsey):
            return If(
                condition,
                jumpify(truthy, label),
                jumpify(falsey, label)
            )
        case _:
            return terminal
