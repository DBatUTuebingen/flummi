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
    condition: grammar.Expression
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


def free_variables(node: Node) -> set[grammar.Variable]:
    match node:
        case Block(_, statements, terminal):
            vars = set()

            for statement in statements:
                vars |= free_variables(statement)

            vars |= free_variables(terminal)

            return vars

        case Emit(expression) | Assignment(_, expression):
            return set(expression.free_variables)

        case If(expression, truthy, falsey):
            return set(expression.free_variables) | free_variables(truthy) | free_variables(falsey)

        case _:
            return set()


def condition_variables(terminal: Terminal) -> set[grammar.Variable]:
    match terminal:
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


def gotoify(terminal: Terminal, label: BlockLabel) -> tuple[Terminal, bool]:
    match terminal:
        case Jump(_label) if _label == label:
            return GoTo(label), True
        case If(condition, truthy, falsey):
            gotoified_truthy, were_jumps_replaced_truthy = gotoify(truthy, label)
            gotoified_falsey, were_jumps_replaced_falsey = gotoify(falsey, label)
            return If(
                condition,
                gotoified_truthy,
                gotoified_falsey
            ), (were_jumps_replaced_truthy or were_jumps_replaced_falsey)
        case _:
            return terminal, False
