from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum, unique, EnumMeta, EnumDict
import re
from typing import Callable

from .errors import PrettyError, Location


class TokensMeta(EnumMeta):
    def __new__(
        metacls, cls: str, bases: tuple[type, ...], classdict: EnumDict
    ) -> TokensMeta:
        new_enum: EnumMeta = super().__new__(metacls, cls, bases, classdict)
        return unique(new_enum)  # pyright: ignore[reportUnknownVariableType, reportArgumentType]


class Tokens(StrEnum, metaclass=TokensMeta): ...


@dataclass
class Token[T: Tokens]:
    type: T
    value: str
    row: int
    column: int

    @property
    def location(self) -> Location:
        return Location(self.row, self.column)


type Lexer[T: Tokens] = Callable[[str], Iterator[Token[T]]]


def make_lexer[T: Tokens](
    types: type[T], skip: set[T] | None = None
) -> Lexer[T]:
    """Build a lexer for a given enum of token types.

    :param types: The enum to build the lexer for.
    :type types: type[T]
    :param skip: A set of token types to emit not tokens for.
    :type skip: set[T]
    :return: The lexer for the given token types.
    :rtype: Lexer[T]
    """

    def lex(code: str) -> Iterator[Token[T]]:
        token_regex = r"|".join(
            rf"(?P<{type.name}>{type.value})" for type in types
        )
        line, line_start, column = 1, 0, 0
        for match in re.finditer(token_regex, code):
            assert match.lastgroup is not None
            type = types[match.lastgroup]  # type: ignore
            value = match.group()
            column = 1 + match.start() - line_start

            if (newlines := len(lines := value.split("\n"))) > 1:
                line_start = match.end() - len(lines[-1])
                line += newlines - 1

            if skip and type in skip:
                continue

            yield Token(type, value, line, column)

    return lex


class ParseError(PrettyError, SyntaxError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


class Parser[T: Tokens]:
    __slots__: tuple[str, ...] = (
        "source",
        "tokens",
        "current",
        "done",
        "prefetched",
    )

    source: str
    tokens: Iterator[Token[T]]
    current: Token[T]
    done: bool
    prefetched: list[Token[T]]

    def __init__(self, source: str, lexer: Lexer[T]):
        self.source = source
        self.tokens = lexer(source)
        self.done = False
        self.prefetched = []
        self.advance()

    def error(self, msg: str):
        """Throw a syntax error based on the current token.

        :param msg: The error message to report.
        :type msg: str
        :raises SyntaxError: The actual error.
        """
        raise ParseError(msg, self.current.location)

    def advance(self):
        """Advance the parser to the next token."""
        if self.done:
            self.error("Tried to advance past the end.")

        if self.prefetched:
            self.current = self.prefetched.pop(0)
        else:
            if (token := self._advance()) is not None:
                self.current = token

    def _advance(self) -> Token[T] | None:
        """Advance the parser to the next token, without regard for prefetched tokens."""
        try:
            return next(self.tokens)
        except StopIteration:
            self.done = True

    def _peek(self, count: int) -> list[T | None]:
        """Peek at the types of upcoming tokens.

        :param count: The number of tokens to peek at.
        :type count: int
        :return: The types of the upcoming tokens.
        :rtype: list[T|None]
        """
        if count <= len(self.prefetched):
            return [token.type for token in self.prefetched[:count]]
        else:
            output: list[T | None] = []
            for _ in range(count):
                if (token := self._advance()) is not None:
                    output.append(token.type)
                    self.prefetched.append(token)
                else:
                    output.append(None)
            return output

    def lookahead(self, *types: T) -> bool:
        """Compare the types upcoming tokens to a given sequence of token types.

        :param *types: The types the upcomming tokens should be.
        :type *types: T
        :return: If the upcomming tokens matched the given types.
        :rtype: bool
        """
        return list(types) == [self.current.type] + self._peek(len(types) - 1)

    def match(self, type: T) -> bool:
        """Advances the parser if the current token is of a given type.

        :param type: The type the current token should be.
        :type type: T
        :return: If the current token matched the given type.
        :rtype: bool
        """
        return self.matchv(type) is not None

    def matchv(self, type: T) -> str | None:
        """Advances the parser if the current token is of a given type and
        extracts its value.

        :param type: The type the current token should be.
        :type type: T
        :return: The value of the current token, if it matched the given type.
        :rtype: str | None
        """
        if (result := self.multi_matchv(type)) is not None:
            _, value = result
            return value

    def multi_match(self, *types: T) -> T | None:
        """Advances the parser if the current token is of any given type.

        :param *type: The types the current token should be.
        :type *type: T
        :return: The type of the current token if it matched any given type.
        :rtype: T | None
        """
        if (result := self.multi_matchv(*types)) is not None:
            found_type, _ = result
            return found_type

    def multi_matchv(self, *types: T) -> tuple[T, str] | None:
        """Advances the parser if the current token is of any given type an
        extracts its value.

        :param *type: The types the current token should be.
        :type *type: T
        :return: The type and value of the current token, if it matched a given type.
        :rtype: tuple[T, str] | None
        """
        if self.done:
            return None

        _types = set(types)
        if self.current.type in _types:
            found_type = self.current.type
            value = self.current.value
            self.advance()
            return found_type, value
        else:
            return None

    def expect(self, type: T, msg: str | None = None):
        """Advances the parser if the current token is of a given type,
        otherwise throw an error.

        :param type: The type the current token should be.
        :type type: T
        """
        _ = self.expectv(type, msg)

    def expectv(self, type: T, msg: str | None = None) -> str:  # type: ignore
        """Advances the parser if the current token is of a given type and
        extracts its value, otherwise throw an error.

        :param type: The type the current token should be.
        :type type: T
        :return: The value of the current token, if it matched the given type.
        :rtype: str | None
        """
        msg = msg or f"Expected {type.name} but found {self.current.type.name}."
        _, value = self.multi_expectv(type, msg=msg)
        return value

    def multi_expect(self, *types: T, msg: str | None = None) -> T:
        """Advances the parser if the current token is of any given type,
        otherwise throw an error.

        :param *type: The types the current token should be.
        :type *type: T
        """
        found_type, _ = self.multi_expectv(*types, msg=msg)
        return found_type

    def multi_expectv(self, *types: T, msg: str | None = None) -> tuple[T, str]:
        """Advances the parser if the current token is of a given type and
        extracts its value, otherwise throw an error.

        :param type: The type the current token should be.
        :type type: T
        :return: The type and value of the current token, if it matched a given type.
        :rtype: tuple[T, str]
        """
        msg = (
            msg
            or f"Expected one of ({', '.join(type.name for type in types)}) but found {self.current.type.name}."
        )
        if (result := self.multi_matchv(*types)) is not None:
            return result
        else:
            raise self.error(msg)

    def sequence[A](
        self,
        parse: Callable[[], A],
        separator: T,
    ) -> Iterator[A]:
        return self.multi_sequence(parse, separator)

    def multi_sequence[A](
        self,
        parse: Callable[[], A],
        *separators: T,
    ) -> Iterator[A]:
        while True:
            yield parse()
            if not self.multi_match(*separators):
                return
