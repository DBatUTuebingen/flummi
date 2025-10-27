from dataclasses import dataclass, field

from ..library.errors import Location

__all__ = (
    "Located",
    "Identifier",
    "Expression",
    "Type",
    "Program",
)


@dataclass(kw_only=True, match_args=False, slots=True)
class Located:
    location: Location = field(hash=False, compare=False, repr=False)


@dataclass(unsafe_hash=True, order=True, slots=True)
class Identifier(Located):
    identifier: str


@dataclass(slots=True)
class Expression(Located):
    source: str
    arguments: list[Identifier]


@dataclass(unsafe_hash=True, order=True, slots=True)
class Type(Located):
    source: str


@dataclass(slots=True)
class Program[B: Located](Located):
    body: B
