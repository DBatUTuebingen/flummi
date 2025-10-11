from __future__ import annotations

from dataclasses import dataclass, field


__all__ = (
    "Annotated",
    "Expression",
    "Identifier",
    "Type",
    "Program",
)


@dataclass(kw_only=True, match_args=False)
class Annotated[A]:
    annotation: A = field(hash=False, compare=False, repr=False)


@dataclass
class Expression[A](Annotated[A]):
    source: str
    arguments: list[Identifier[A]]


@dataclass(unsafe_hash=True, order=True)
class Identifier[A](Annotated[A]):
    identifier: str


@dataclass
class Type[A](Annotated[A]):
    source: str


@dataclass
class Program[A, B](Annotated[A]):
    body: B
