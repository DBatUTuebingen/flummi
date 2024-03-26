from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field

from . import AST
from ..utils import *

__all__ = (
    "Label",
    "Graph",
    "Block",
    "Action",
    "Assignments",
    "Nothing",
    "Wait",
    "Assignment",
    "Terminal",
    "TerminalType",
    "Call",
    "Return",
    "Jump",
    "GoTo",
)


@dataclass(unsafe_hash=True)
class Label:
    label: str


@dataclass
class Graph:
    entry_label: Label
    initialising_assignment: Assignment | None
    blocks: dict[Label, Block]


@dataclass
class Block:
    label: Label
    action: Action
    terminals: list[Terminal]


class Action(ABC):
    ...


@dataclass
class Nothing(Action):
    ...


@dataclass
class Wait(Action):
    handle: Label
    targets: list[AST.Variable]


@dataclass
class Assignments(Action):
    assignments: list[Assignment]


@dataclass
class Assignment:
    variables: list[AST.Variable]
    expression: AST.Expression


@dataclass
class Terminal[T]:
    type: T
    truthy: list[AST.Variable] = field(default_factory=list)
    falsey: list[AST.Variable] = field(default_factory=list)


class TerminalType(ABC):
    ...

@dataclass
class Return(TerminalType):
    variables: list[AST.Variable]


@dataclass
class Jump(TerminalType):
    target: Label


@dataclass
class GoTo(TerminalType):
    target: Label


@dataclass
class Call(TerminalType):
    handle: Label
    target: Label
    arguments: list[AST.Variable]


type Node = Graph | Block | Action | Assignment | Terminal | TerminalType


def successors(block: Block) -> set[Label]:
    return {
        terminal.type.target
        for terminal in block.terminals
        if isinstance(terminal.type, (Jump, GoTo))
    }


def jumps(block: Block) -> set[Label]:
    return {
        terminal.type.target
        for terminal in block.terminals
        if isinstance(terminal.type, Jump)
    }


def gotos(block: Block) -> set[Label]:
    return {
        terminal.type.target
        for terminal in block.terminals
        if isinstance(terminal.type, GoTo)
    }


def calls(block: Block) -> set[Label]:
    return {
        terminal.type.target
        for terminal in block.terminals
        if isinstance(terminal.type, Call)
    }


def returns(block: Block) -> list[Return]:
    return [
        terminal.type
        for terminal in block.terminals
        if isinstance(terminal.type, Return)
    ]


def emited_variables(block: Block) -> list[AST.Variable]:
    return sum(
        (
            emit.variables
            for emit in returns(block)
        ),
        start=[]
    )


def contains_jumps(block: Block) -> bool:
    return bool(jumps(block))


def contains_emits(block: Block) -> bool:
    return bool(returns(block))


def free_variables(node: Node) -> set[AST.Variable]:
    match node:
        case Block(_, action, terminals):
            assigned = bound_variables(node)
            vars = free_variables(action)

            for terminal in terminals:
                vars |= free_variables(terminal) - assigned

            return vars

        case Terminal(type, truthy, falsey):
            return {*truthy, *falsey} | free_variables(type)

        case Return(variables):
            return set(variables)

        case Assignment(_, expression):
            return set(expression.free_variables)

        case Assignments(assignments):
            vars = set()
            for assignment in assignments:
                vars |= free_variables(assignment)
            return vars

        case _:
            return set()


def condition_variables(terminal: Terminal) -> set[AST.Variable]:
    match terminal:
        case Terminal(_, truthy, falsey):
            return {*truthy, *falsey}
        case _:
            return set()


def bound_variables(block: Block) -> set[AST.Variable]:
    if isinstance(block.action, Assignments):
        return union(
            assignment.variables
            for assignment in block.action.assignments
        )
    else:
        return set()
