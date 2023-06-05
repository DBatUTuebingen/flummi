from dataclasses import dataclass
from typing import Generic, TypeVar, Protocol, runtime_checkable

__all__ = (
    "SupportsStr",
    "SupportsFormat",
    "Variable",
    "Expression",
    "Type",
)


@runtime_checkable
class SupportsStr(Protocol):
    def __str__(self) -> str:
        ...

@runtime_checkable
class SupportsFormat(Protocol):
    def format(self, *args: str) -> str:
        ...

E = TypeVar("E", bound=SupportsFormat)
T = TypeVar("T", bound=SupportsStr)


@dataclass
class Variable:
    identifier: str

    def __hash__(self) -> int:
        return hash(self.identifier)

    def __str__(self) -> str:
        return self.identifier


@dataclass
class Expression(Generic[E]):
    source: E
    free_variables: list[Variable]

    def __str__(self) -> str:
        return f"§{self.source!s}§[{', '.join(map(str, self.free_variables))}]"


@dataclass
class Type(Generic[T]):
    source: T

    def __str__(self) -> str:
        return f"§{self.source!s}§"
