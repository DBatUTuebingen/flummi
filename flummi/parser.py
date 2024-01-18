from dataclasses import dataclass, field
from enum import Enum, unique
import re
from textwrap import dedent
from typing import Callable, Iterator

from . import grammar


__all__ = (
    "parse",
)


def parse(source: str) -> grammar.Program:
    token_stream = tokenize(source)
    return Parser(token_stream).parse_program()


@unique
class TokenType(Enum):
    LEFT_PAREN = r"\("
    LEFT_BRACE = r"{"
    LEFT_BRACKET = r"\["
    LEFT_ARROW = r"<-"
    RIGHT_PAREN = r"\)"
    RIGHT_BRACE = r"}"
    RIGHT_BRACKET = r"\]"
    RIGHT_ARROW = r"->"
    COLON = r":"
    SEMICOLON = r";"
    COMMA = r","
    EXTERNAL = r"[§][^§]+[§]"
    IF = r"IF"
    CALL = r"CALL"
    IN = r"IN"
    FUN = r"FUN"
    LOOP = r"LOOP"
    CONTINUE = r"CONTINUE"
    BREAK = r"BREAK"
    THEN = r"THEN"
    ELSE = r"ELSE"
    EMIT = r"EMIT"
    STOP = r"STOP"
    NOOP = r"NOOP"
    IDENTIFIER = r"[a-zA-Z_][a-zA-Z_0-9]*"
    COMMENT = r"--[^\n]*"
    NEWLINE = r"\n"
    WHITESPACE = r"\s+"


@dataclass
class Token:
    token_type: TokenType
    value: str
    line: int
    column: int


def tokenize(code: str) -> Iterator[Token]:
    token_regex = r'|'.join(fr'(?P<{token_type.name}>{token_type.value})' for token_type in TokenType)
    line, line_start, column = 1, 0, 0
    for match in re.finditer(token_regex, code):
        token_type = TokenType[match.lastgroup]  # type: ignore
        value = match.group()
        column = match.start() - line_start
        if token_type in {TokenType.NEWLINE}:
            line_start = match.end()
            line += 1
            continue

        elif token_type in {TokenType.WHITESPACE, TokenType.COMMENT}:
            continue

        yield Token(token_type, value, line, column)


@dataclass
class Parser:
    stream: Iterator[Token]
    _done: bool = False
    current: Token = field(init=False)
    prefetched: list[Token] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.advance()

    def error(self, msg: str) -> SyntaxError:
        return SyntaxError(
            msg + f" (at {self.current.line}:{self.current.column})",
            self.current.line,
            self.current.column,
        )

    @property
    def done(self) -> bool:
        return self._done and not self.prefetched

    def advance(self):
        if self.prefetched:
            self.current = self.prefetched.pop(0)
        else:
            if (token := self._advance()) is not None:
                self.current = token

    def _advance(self) -> Token|None:
        try:
            return next(self.stream)
        except StopIteration:
            self._done = True

    def peek(self, count: int) -> list[TokenType|None]:
        if count <= len(self.prefetched):
            return [token.token_type for token in self.prefetched[:count]]
        else:
            output = []
            for _ in range(count):
                if (token := self._advance()) is not None:
                    output.append(token.token_type)
                    self.prefetched.append(token)
                else:
                    output.append(None)
            return output

    def lookahead(self, *token_types: TokenType) -> bool:
        return list(token_types) == [self.current.token_type] + self.peek(len(token_types) - 1)

    def match(self, token_type: TokenType) -> bool:
        if not self.done and self.current.token_type == token_type:
            self.advance()
            return True
        else:
            return False

    def matchv(self, token_type: TokenType) -> str | None:
        if not self.done and self.current.token_type == token_type:
            value = self.current.value
            self.advance()
            return value
        else:
            return None

    def expect(self, token_type: TokenType, msg: str | None = None):
        if not self.match(token_type):
            raise self.error(msg or f"Expected {token_type.name}, found {self.current.token_type.name}")

    def expectv(self, token_type: TokenType, msg: str | None = None) -> str:
        if (value := self.matchv(token_type)) is not None:
            return value
        else:
            raise self.error(msg or f"Expected {token_type.name}, found {self.current.token_type.name}")

    def sequence[T](self, separator_type: TokenType, parser: Callable[[], T]) -> Iterator[T]:
        while True:
            yield parser()
            if not self.match(separator_type):
                return

    def parse_expression(self) -> grammar.Expression:
        value = self.expectv(TokenType.EXTERNAL)[1:-1]
        self.expect(TokenType.LEFT_BRACKET)
        if self.match(TokenType.RIGHT_BRACKET):
            free_variables = []
        else:
            free_variables = list(self.sequence(TokenType.COMMA, self.parse_variable))
            self.expect(TokenType.RIGHT_BRACKET)
        return grammar.Expression(
            source=dedent(value).strip(),
            free_variables=free_variables
        )

    def parse_variable(self) -> grammar.Variable:
        identifier = self.expectv(TokenType.IDENTIFIER)
        return grammar.Variable(
            identifier=identifier
        )

    def parse_type(self) -> grammar.Type:
        value = self.expectv(TokenType.EXTERNAL)[1:-1]
        return grammar.Type(
            source=value
        )

    def parse_program(self) -> grammar.Program:
        self.expect(TokenType.CALL)
        self.expect(TokenType.LEFT_PAREN)
        if self.match(TokenType.RIGHT_PAREN):
            inputs = []
        else:
          inputs = list(self.sequence(TokenType.COMMA, self.parse_expression))
          self.expect(TokenType.RIGHT_PAREN)
        self.expect(TokenType.IN)
        function = self.parse_function()
        return grammar.Program(
            inputs=inputs,
            function=function
        )

    def parse_function(self) -> grammar.Function:
        self.expect(TokenType.FUN)
        self.expect(TokenType.LEFT_PAREN)
        if self.match(TokenType.RIGHT_PAREN):
            parameters = {}
        else:
            parameters = {
                declaration.variable: declaration.type
                for declaration in self.sequence(TokenType.COMMA, self.parse_declaration)
            }
            self.expect(TokenType.RIGHT_PAREN)
        self.expect(TokenType.RIGHT_ARROW)
        emits = self.parse_type()
        self.expect(TokenType.COLON)
        body = self.parse_statement()

        return grammar.Function(
            parameters=parameters,
            emits=emits,
            body=body
        )

    def parse_statement(self) -> grammar.Statement:
        if self.lookahead(TokenType.LOOP):
            return self.parse_loop()
        elif self.lookahead(TokenType.CONTINUE):
            return self.parse_continue()
        elif self.lookahead(TokenType.BREAK):
            return self.parse_break()
        elif self.lookahead(TokenType.IF):
            return self.parse_if()
        elif self.lookahead(TokenType.EMIT):
            return self.parse_emit()
        elif self.lookahead(TokenType.IDENTIFIER, TokenType.COLON):
            return self.parse_declaration()
        elif self.lookahead(TokenType.IDENTIFIER, TokenType.LEFT_ARROW):
            return self.parse_assignment()
        elif self.lookahead(TokenType.LEFT_BRACE):
            return self.parse_block()
        elif self.lookahead(TokenType.STOP):
            return self.parse_stop()
        elif self.lookahead(TokenType.NOOP):
            return self.parse_noop()
        else:
            raise self.error("Expected statement")

    def parse_loop(self) -> grammar.Loop:
        self.expect(TokenType.LOOP)
        name = self.expectv(TokenType.IDENTIFIER)
        body = self.parse_statement()
        return grammar.Loop(
            name=name,
            body=body
        )

    def parse_continue(self) -> grammar.Continue:
        self.expect(TokenType.CONTINUE)
        name = self.expectv(TokenType.IDENTIFIER)
        return grammar.Continue(name)

    def parse_break(self) -> grammar.Break:
        self.expect(TokenType.BREAK)
        name = self.expectv(TokenType.IDENTIFIER)
        return grammar.Break(name)

    def parse_if(self) -> grammar.If:
        self.expect(TokenType.IF)
        condition = self.parse_variable()
        self.expect(TokenType.THEN)
        truthy_branch = self.parse_statement()
        self.expect(TokenType.ELSE)
        falsey_branch = self.parse_statement()
        return grammar.If(
            condition=condition,
            truthy_branch=truthy_branch,
            falsey_branch=falsey_branch
        )

    def parse_emit(self) -> grammar.Emit:
        self.expect(TokenType.EMIT)
        to_emit = self.parse_expression()
        return grammar.Emit(
            to_emit=to_emit
        )

    def parse_declaration(self) -> grammar.Declaration:
        variable = self.parse_variable()
        self.expect(TokenType.COLON)
        type = self.parse_type()
        return grammar.Declaration(
            variable=variable,
            type=type
        )

    def parse_assignment(self) -> grammar.Assignment:
        variable = self.parse_variable()
        self.expect(TokenType.LEFT_ARROW)
        expression = self.parse_expression()
        return grammar.Assignment(
            variable=variable,
            expression=expression
        )

    def parse_block(self) -> grammar.Block:
        self.expect(TokenType.LEFT_BRACE)
        if self.match(TokenType.RIGHT_BRACE):
            statements = []
        else:
            statements = list(self.sequence(TokenType.SEMICOLON, self.parse_statement))
            self.expect(TokenType.RIGHT_BRACE)
        return grammar.Block(
            statements=statements
        )

    def parse_stop(self) -> grammar.Stop:
        self.expect(TokenType.STOP)
        return grammar.Stop()

    def parse_noop(self) -> grammar.NoOp:
        self.expect(TokenType.NOOP)
        return grammar.NoOp()
