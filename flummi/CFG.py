from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field

from . import grammar

__all__ = (
    "BlockLabel",
    "Graph",
    "Block",
    "Action",
    "SpanningAssignments",
    "ReducingAssignment",
    "Terminal",
    "TerminalType",
    "GoTo",
    "Emit",
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
    action: Action | None
    terminals: list[Terminal]


class Action(ABC):
    ...


@dataclass
class SpanningAssignments(Action):
    assignments: list[grammar.Assignment]


@dataclass
class ReducingAssignment(Action):
    assignment: grammar.Assignment


@dataclass
class Terminal:
    type: TerminalType
    truthy: list[grammar.Variable] = field(default_factory=list)
    falsey: list[grammar.Variable] = field(default_factory=list)


class TerminalType(ABC):
    ...


@dataclass
class GoTo(TerminalType):
    target: BlockLabel


@dataclass
class Emit(TerminalType):
    emit: grammar.Emit


def successors(block: Block) -> set[BlockLabel]:
    return {
        terminal.type.target
        for terminal in block.terminals
        if isinstance(terminal.type, GoTo)
    }


def emits(block: Block) -> list[Emit]:
    return [
        terminal.type
        for terminal in block.terminals
        if isinstance(terminal.type, Emit)
    ]


def emited_variables(block: Block) -> set[grammar.Variable]:
    return set(sum(
        (
            emit.emit.to_emit
            for emit in emits(block)
        ),
        start=[]
    ))


def contains_emits(block: Block) -> bool:
    return bool(emits(block))


def free_variables(node: Block | Terminal | Emit | TerminalType | Action) -> set[grammar.Variable]:
    match node:
        case Block(_, action, terminals):
            if action is not None:
                vars = free_variables(action)
                assigned = bound_variables(action)
            else:
                vars, assigned = set(), set()

            for terminal in terminals:
                vars |= free_variables(terminal) - assigned

            return vars

        case Terminal(type, truthy, falsey):
            return {*truthy, *falsey} | free_variables(type)

        case Emit(emit):
            return set(emit.to_emit)

        case SpanningAssignments(assignments):
            vars = set()
            for assignment in assignments:
                vars |= {
                    argument.variable
                    for argument in assignment.expression.arguments
                }
            return vars

        case ReducingAssignment(assignment):
            return {
                argument.variable
                for argument in assignment.expression.arguments
            }

        case _:
            return set()


def condition_variables(terminal: Terminal) -> set[grammar.Variable]:
    match terminal:
        case Terminal(_, truthy, falsey):
            return {*truthy, *falsey}
        case _:
            return set()


def bound_variables(node: Block | Action) -> set[grammar.Variable]:
    match node:
        case Block(_, action, _):
            if action is not None:
                return bound_variables(action)
            else:
                return set()

        case SpanningAssignments(assignments):
            vars = set()
            for assignment in assignments:
                vars.update(assignment.variables)
            return vars

        case ReducingAssignment(assignment):
            return set(assignment.variables)

        case _:
            return set()

