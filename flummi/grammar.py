from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, unique


__all__ = (
    "Location",
    "Variable",
    "Valuedness",
    "Expression",
    "Argument",
    "Type",
    "Program",
    "Function",
    "Statement",
    "If",
    "Emit",
    "Stop",
    "Declaration",
    "Assignment",
    "Block",
    "NoOp",
)



@dataclass
class Location:
    line: int
    column: int


@dataclass
class Node:
    location: Location = field(hash=False, compare=False)


@dataclass(unsafe_hash=True)
class Variable(Node):
    identifier: str


@unique
class Valuedness(Enum):
    SCALAR = "ONE"
    SET = "MANY"


@dataclass
class Expression(Node):
    valuedness: Valuedness
    source: str
    arguments: list[Argument]


@dataclass
class Argument(Node):
    valuedness: Valuedness
    variable: Variable


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
    valuedness: Valuedness
    emits: tuple[Type, ...]
    body: Statement


class Statement(Node):
    ...


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
    variable: Variable
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
