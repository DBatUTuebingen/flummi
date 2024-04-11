from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field

from . import common
from ..utils import *

__all__ = (
    "Function",
    "Program",
    "Handle",
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




type Program[A] = common.Program[A, Graph[A]]
type Function[A] = common.Function[A, Graph[A]]
type Label[A] = common.Identifier[A]
type Handle[A] = common.Identifier[A]



@dataclass
class Graph[A](common.Annotated[A]):
    entry_label: Label
    blocks: dict[Label, Block]


@dataclass
class Block[A](common.Annotated[A]):
    label: Label
    action: Action
    terminals: list[Terminal]


class Action[A](common.Annotated[A], ABC):
    ...


@dataclass
class Nothing[A](Action[A]):
    ...


@dataclass
class Waits[A](Action[A]):
    waits: list[Wait[A]]


@dataclass
class Wait[A](common.Annotated[A]):
    handle: common.Identifier[A]
    targets: list[common.Identifier[A]]


@dataclass
class Assignments[A](Action[A]):
    assignments: list[Assignment]


@dataclass
class Assignment[A](common.Annotated[A]):
    variables: list[common.Identifier[A]]
    expression: common.Expression[A]


@dataclass
class Terminal[A](common.Annotated[A]):
    type: TerminalType[A]
    truthy: list[common.Identifier[A]] = field(default_factory=list)
    falsey: list[common.Identifier[A]] = field(default_factory=list)


class TerminalType[A](common.Annotated[A], ABC):
    ...


@dataclass
class Return[A](TerminalType[A]):
    variables: list[common.Identifier[A]]


@dataclass
class Jump[A](TerminalType[A]):
    target: Label[A]


@dataclass
class GoTo[A](TerminalType[A]):
    target: Label[A]


@dataclass
class Call[A](TerminalType[A]):
    handle: Handle[A]
    target: Label[A]
    arguments: list[common.Identifier[A]]


type Node[A] = (
    Graph[A] |
    Block[A] |
    Action[A] |
    Assignment[A] |
    Terminal[A] |
    TerminalType[A]
)


def successors[A](block: Block[A]) -> set[Label[A]]:
    return {
        terminal.type.target
        for terminal in block.terminals
        if isinstance(terminal.type, (Jump, GoTo))
    }


def jumps[A](block: Block[A]) -> set[Label[A]]:
    return {
        terminal.type.target
        for terminal in block.terminals
        if isinstance(terminal.type, Jump)
    }


def gotos[A](block: Block[A]) -> set[Label[A]]:
    return {
        terminal.type.target
        for terminal in block.terminals
        if isinstance(terminal.type, GoTo)
    }


def calls[A](block: Block[A]) -> set[Label[A]]:
    return {
        terminal.type.target
        for terminal in block.terminals
        if isinstance(terminal.type, Call)
    }


def returns[A](block: Block[A]) -> list[Return[A]]:
    return [
        terminal.type
        for terminal in block.terminals
        if isinstance(terminal.type, Return)
    ]


def emited_variables[A](block: Block[A]) -> list[common.Identifier[A]]:
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


def free_variables[A](node: Node[A]) -> set[common.Identifier[A]]:
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
            return set(expression.arguments)

        case Assignments(assignments):
            vars = set()
            for assignment in assignments:
                vars |= free_variables(assignment)
            return vars

        case _:
            return set()


def condition_variables[A](terminal: Terminal[A]) -> set[common.Identifier[A]]:
    match terminal:
        case Terminal(_, truthy, falsey):
            return {*truthy, *falsey}
        case _:
            return set()


def bound_variables[A](block: Block[A]) -> set[common.Identifier[A]]:
    if isinstance(block.action, Assignments):
        return union(
            assignment.variables
            for assignment in block.action.assignments
        )
    else:
        return set()
