from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field

from . import grammar
from .utils import *

__all__ = (
    "BlockLabel",
    "Graph",
    "Block",
    "Assignment",
    "Terminal",
    "TerminalType",
    "Emit",
    "Jump",
    "GoTo",
)


@dataclass(unsafe_hash=True)
class BlockLabel:
    label: str


@dataclass
class Graph:
    entry_label: BlockLabel
    initialising_assignment: Assignment | None
    blocks: dict[BlockLabel, Block]


@dataclass
class Block:
    label: BlockLabel
    assignments: list[Assignment]
    terminals: list[Terminal]


@dataclass
class Assignment:
    variables: list[grammar.Variable]
    expression: grammar.Expression


@dataclass
class Terminal[T]:
    type: T
    truthy: list[grammar.Variable] = field(default_factory=list)
    falsey: list[grammar.Variable] = field(default_factory=list)


class TerminalType(ABC):
    ...

@dataclass
class Emit(TerminalType):
    to_emit: list[grammar.Variable]


@dataclass
class Jump(TerminalType):
    label: BlockLabel


@dataclass
class GoTo(TerminalType):
    label: BlockLabel


type Node = Graph | Block | Assignment | Emit | Terminal | TerminalType


def successors(block: Block) -> set[BlockLabel]:
    return {
        terminal.type.label
        for terminal in block.terminals
        if isinstance(terminal.type, (Jump, GoTo))
    }


def jumps(block: Block) -> set[BlockLabel]:
    return {
        terminal.type.label
        for terminal in block.terminals
        if isinstance(terminal.type, Jump)
    }


def gotos(block: Block) -> set[BlockLabel]:
    return {
        terminal.type.label
        for terminal in block.terminals
        if isinstance(terminal.type, GoTo)
    }


def emits(block: Block) -> list[Emit]:
    return [
        terminal.type
        for terminal in block.terminals
        if isinstance(terminal.type, Emit)
    ]


def emited_variables(block: Block) -> list[grammar.Variable]:
    return sum(
        (
            emit.to_emit
            for emit in emits(block)
        ),
        start=[]
    )


def contains_jumps(block: Block) -> bool:
    return bool(jumps(block))


def contains_emits(block: Block) -> bool:
    return bool(emits(block))


def free_variables(node: Node) -> set[grammar.Variable]:
    match node:
        case Block(_, assignments, terminals):
            assigned, vars = set(), set()

            for assignment in assignments:
                assigned.update(assignment.variables)
                vars |= free_variables(assignment)

            for terminal in terminals:
                vars |= free_variables(terminal) - assigned

            return vars

        case Terminal(type, truthy, falsey):
            return {*truthy, *falsey} | free_variables(type)

        case Emit(to_emit):
            return set(to_emit)

        case Assignment(_, expression):
            return set(expression.free_variables)

        case _:
            return set()


def condition_variables(terminal: Terminal) -> set[grammar.Variable]:
    match terminal:
        case Terminal(_, truthy, falsey):
            return {*truthy, *falsey}
        case _:
            return set()


def bound_variables(block: Block) -> set[grammar.Variable]:
    return union(
        assignment.variables
        for assignment in block.assignments
    )
