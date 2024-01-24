from __future__ import annotations
from abc import ABC
from dataclasses import dataclass


__all__ = (
    "Variable",
    "Expression",
    "Type",
    "Program",
    "Function",
    "Statement",
    "Loop",
    "Continue",
    "Break",
    "If",
    "Emit",
    "Stop",
    "Declaration",
    "Assignment",
    "Block",
    "NoOp",
)



@dataclass
class Variable:
    identifier: str

    def __hash__(self) -> int:
        return hash(self.identifier)

    def __str__(self) -> str:
        return self.identifier


@dataclass
class Expression:
    source: str
    free_variables: list[Variable]

    def __str__(self) -> str:
        return f"§{self.source!s}§[{', '.join(map(str, self.free_variables))}]"


@dataclass
class Type:
    source: str

    def __str__(self) -> str:
        return f"§{self.source!s}§"


@dataclass
class Program:
    inputs: list[Expression]
    function: Function


@dataclass
class Function:
    parameters: dict[Variable, Type]
    emits: Type
    body: Statement


class Statement(ABC):
    ...


@dataclass
class Loop(Statement):
    name: str
    body: Statement


@dataclass
class Continue(Statement):
    name: str


@dataclass
class Break(Statement):
    name: str


@dataclass
class If(Statement):
    condition: Expression
    truthy_branch: Statement
    falsey_branch: Statement


@dataclass
class Emit(Statement):
    to_emit: Expression


@dataclass
class Stop(Statement):
    ...


@dataclass
class Declaration(Statement):
    variable: Variable
    type: Type


@dataclass
class Assignment(Statement):
    variable: Variable
    expression: Expression


@dataclass
class Block(Statement):
    statements: list[Statement]


@dataclass
class NoOp(Statement):
    ...
