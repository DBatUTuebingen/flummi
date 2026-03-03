from __future__ import annotations

from dataclasses import dataclass, field

from ..library.errors import Location

__all__ = (
    "Located",
    "Expression",
    "Identifier",
    "Variable",
    "Label",
    "Type",
    "Program",
)


@dataclass(kw_only=True, match_args=False, slots=True)
class Located:
    location: Location = field(hash=False, compare=False, repr=False)


@dataclass(unsafe_hash=True, order=True, slots=True)
class Identifier(Located):
    identifier: str


Variable = Identifier
Label = Identifier


@dataclass(slots=True)
class Expression(Located):
    source: str
    arguments: list[Variable]


@dataclass(unsafe_hash=True, order=True, slots=True)
class Type(Located):
    source: str


@dataclass(slots=True)
class Program[B](Located):
    body: B
