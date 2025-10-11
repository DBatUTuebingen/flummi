from __future__ import annotations

from dataclasses import dataclass, field

from ..library.errors import Location

__all__ = (
    "Located",
    "Expression",
    "Identifier",
    "Type",
    "Program",
)


@dataclass(kw_only=True, match_args=False)
class Located:
    location: Location = field(hash=False, compare=False, repr=False)


@dataclass
class Expression(Located):
    source: str
    arguments: list[Identifier]


@dataclass(unsafe_hash=True, order=True)
class Identifier(Located):
    identifier: str


@dataclass
class Type(Located):
    source: str


@dataclass
class Program[B](Located):
    body: B
