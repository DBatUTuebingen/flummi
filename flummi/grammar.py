from __future__ import annotations
from dataclasses import dataclass, field


__all__ = (
    "Location",
    "Variable",
    "Expression",
    "Type",
    "Program",
    "Function",
    "Statement",
    "If",
    "Loop",
    "Break",
    "Continue",
    "Emit",
    "Stop",
    "Declaration",
    "Assignment",
    "Block",
    "NoOp",
)



@dataclass(unsafe_hash=True, order=True)
class Location:
    line: int
    column: int


@dataclass
class Node:
    location: Location = field(hash=False, compare=False)


@dataclass(unsafe_hash=True, order=True)
class Variable(Node):
    identifier: str


@dataclass
class Expression(Node):
    source: str
    free_variables: list[Variable]


@dataclass
class Type(Node):
    source: str


@dataclass
class Program(Node):
    inputs: Expression | None
    function: Function


@dataclass
class Function(Node):
    parameters: dict[Variable, Type]
    emits: list[Type]
    body: Statement


class Statement(Node):
    ...


@dataclass
class Loop(Statement):
    name: Variable
    body: Statement


@dataclass
class Continue(Statement):
    name: Variable


@dataclass
class Break(Statement):
    name: Variable


@dataclass
class If(Statement):
    condition: Variable
    truthy_branch: Statement
    falsey_branch: Statement


@dataclass
class Emit(Statement):
    to_emit: list[Variable]


@dataclass
class Stop(Statement):
    ...


@dataclass
class Declaration(Statement):
    variables: list[Variable]
    type: Type


@dataclass
class Assignment(Statement):
    variables: list[Variable]
    expression: Expression


@dataclass
class Block(Statement):
    statements: list[Statement]


@dataclass
class NoOp(Statement):
    ...
