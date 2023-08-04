from dataclasses import dataclass, field
from enum import Enum, unique
import re
from textwrap import dedent
from typing import Callable, Iterator, TypeVar

from .grammars import proc, common


__all__ = (
    "parse",
)


T = common.T
K = TypeVar("K")


def parse(source: str) -> proc.Program[str, str]:
    token_stream = tokenize(source)
    return Parser(token_stream).parse_program()


@unique
class TokenType(Enum):
    LEFT_PAREN = r"\("
    LEFT_BRACE = r"{"
    LEFT_BRACKET = r"\["
    LEFT_ARROW = r"<-|←"
    RIGHT_PAREN = r"\)"
    RIGHT_BRACE = r"}"
    RIGHT_BRACKET = r"\]"
    RIGHT_ARROW = r"->|→"
    COLON = r":"
    SEMICOLON = r";"
    COMMA = r","
    EXTERNAL = r"[§⎡][^§⎦]+[§⎦]"
    IF = r"IF|𝗜𝗙"
    CALL = r"CALL|𝗖𝗔𝗟𝗟"
    IN = r"IN|𝗜𝗡"
    FUN = r"FUN|𝗙𝗨𝗡"
    LOOP = r"LOOP|𝗟𝗢𝗢𝗣"
    CONTINUE = r"CONTINUE|𝗖𝗢𝗡𝗧𝗜𝗡𝗨𝗘"
    BREAK = r"BREAK|𝗕𝗥𝗘𝗔𝗞"
    THEN = r"THEN|𝗧𝗛𝗘𝗡"
    ELSE = r"ELSE|𝗘𝗟𝗦𝗘"
    EMIT = r"EMIT|𝗘𝗠𝗜𝗧"
    STOP = r"STOP|𝗦𝗧𝗢𝗣"
    IDENTIFIER = r"[a-zA-Z_][a-zA-Z_0-9]*"
    COMMENT = r"--[^\n]*"
    NEWLINE = r"\n+"
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

    def sequence(self, separator_type: TokenType, parser: Callable[[], K]) -> Iterator[K]:
        while True:
            yield parser()
            if not self.match(separator_type):
                return

    def parse_expression(self) -> common.Expression[str]:
        value = self.expectv(TokenType.EXTERNAL)[1:-1]
        self.expect(TokenType.LEFT_BRACKET)
        if self.match(TokenType.RIGHT_BRACKET):
            free_variables = []
        else:
            free_variables = list(self.sequence(TokenType.COMMA, self.parse_variable))
            self.expect(TokenType.RIGHT_BRACKET)
        return common.Expression(
            source=dedent(value).strip(),
            free_variables=free_variables
        )

    def parse_variable(self) -> common.Variable:
        identifier = self.expectv(TokenType.IDENTIFIER)
        return common.Variable(
            identifier=identifier
        )

    def parse_type(self) -> common.Type[str]:
        value = self.expectv(TokenType.EXTERNAL)[1:-1]
        return common.Type(
            source=value
        )

    def parse_program(self) -> proc.Program[str, str]:
        self.expect(TokenType.CALL)
        self.expect(TokenType.LEFT_PAREN)
        if self.match(TokenType.RIGHT_PAREN):
            inputs = []
        else:
          inputs = list(self.sequence(TokenType.COMMA, self.parse_expression))
          self.expect(TokenType.RIGHT_PAREN)
        self.expect(TokenType.IN)
        function = self.parse_function()
        return proc.Program(
            inputs=inputs,
            function=function
        )

    def parse_function(self) -> proc.Function[str, str]:
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

        return proc.Function(
            parameters=parameters,
            emits=emits,
            body=body
        )

    def parse_statement(self) -> proc.Statement[str, str]:
        if self.match(TokenType.LOOP):
            return self.parse_loop()
        elif self.match(TokenType.CONTINUE):
            return self.parse_continue()
        elif self.match(TokenType.BREAK):
            return self.parse_break()
        elif self.match(TokenType.IF):
            return self.parse_if()
        elif self.match(TokenType.EMIT):
            return self.parse_emit()
        elif self.lookahead(TokenType.IDENTIFIER, TokenType.COLON):
            return self.parse_declaration()
        elif self.lookahead(TokenType.IDENTIFIER, TokenType.LEFT_ARROW):
            return self.parse_assignment()
        elif self.match(TokenType.LEFT_BRACE):
            return self.parse_block()
        elif self.match(TokenType.STOP):
            return self.parse_stop()
        else:
            raise self.error("Expected statement")

    def parse_loop(self) -> proc.Loop[str, str]:
        body = self.parse_statement()
        return proc.Loop(
            body=body
        )

    def parse_continue(self) -> proc.Continue[str, str]:
        return proc.Continue()

    def parse_break(self) -> proc.Break[str, str]:
        return proc.Break()

    def parse_if(self) -> proc.If[str, str]:
        condition = self.parse_expression()
        self.expect(TokenType.THEN)
        truthy_branch = self.parse_statement()
        self.expect(TokenType.ELSE)
        falsey_branch = self.parse_statement()
        return proc.If(
            condition=condition,
            truthy_branch=truthy_branch,
            falsey_branch=falsey_branch
        )

    def parse_emit(self) -> proc.Emit[str, str]:
        to_emit = self.parse_expression()
        return proc.Emit(
            to_emit=to_emit
        )

    def parse_declaration(self) -> proc.Declaration[str, str]:
        variable = self.parse_variable()
        self.expect(TokenType.COLON)
        type = self.parse_type()
        return proc.Declaration(
            variable=variable,
            type=type
        )

    def parse_assignment(self) -> proc.Assignment[str, str]:
        variable = self.parse_variable()
        self.expect(TokenType.LEFT_ARROW)
        expression = self.parse_expression()
        return proc.Assignment(
            variable=variable,
            expression=expression
        )

    def parse_block(self) -> proc.Block[str, str]:
        if self.match(TokenType.RIGHT_BRACE):
            statements = []
        else:
            statements = list(self.sequence(TokenType.SEMICOLON, self.parse_statement))
            self.expect(TokenType.RIGHT_BRACE)
        return proc.Block(
            statements=statements
        )

    def parse_stop(self) -> proc.Stop[str, str]:
        return proc.Stop()
