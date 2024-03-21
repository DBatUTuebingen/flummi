from dataclasses import dataclass, field
from enum import Enum, unique
import re
from textwrap import dedent
from typing import Callable, Iterator

from . import grammar, errors


__all__ = (
    "parse",
)


class ParserError(errors.FlummiError, name="parsing"):
    ...


def parse(source: str) -> grammar.Program:
    token_stream = tokenize(source)
    return Parser(token_stream).parse_program()


@unique
class TokenType(Enum):
    LEFT_PAREN = r"\("
    LEFT_BRACE = r"{"
    LEFT_BRACKET = r"\["
    LEFT_ARROW = r"<-"
    DOUBLE_LEFT_ARROW = r"<="
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
    AS = r"AS"
    FUN = r"FUN"
    LOOP = r"LOOP"
    CONTINUE = r"CONTINUE"
    BREAK = r"BREAK"
    THEN = r"THEN"
    ELSE = r"ELSE"
    RETURN = r"RETURN"
    NOOP = r"NOOP"
    IDENTIFIER = r"\w+"
    COMMENT = r"--[^\n]*"
    WHITESPACE = r"\s+"


@dataclass
class Token:
    token_type: TokenType
    value: str
    line: int
    column: int

    @property
    def location(self) -> grammar.Location:
        return grammar.Location(self.line, self.column)


def tokenize(code: str) -> Iterator[Token]:
    token_regex = r'|'.join(fr'(?P<{token_type.name}>{token_type.value})' for token_type in TokenType)
    line, line_start, column = 1, 0, 0
    for match in re.finditer(token_regex, code):
        token_type = TokenType[match.lastgroup]  # type: ignore
        value = match.group()
        column = match.start() - line_start
        if (newlines := len(lines := value.split("\n"))) > 1:
          line_start = match.end() - len(lines[-1])
          line += newlines - 1

        if token_type in {TokenType.WHITESPACE, TokenType.COMMENT}:
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

    def error(self, msg: str) -> ParserError:
        return ParserError(
            msg,
            self.current.location,
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
        location = self.current.location
        value = self.expectv(TokenType.EXTERNAL)[1:-1]
        self.expect(TokenType.LEFT_BRACKET)
        if self.match(TokenType.RIGHT_BRACKET):
            free_variables = []
        else:
            free_variables = list(self.sequence(TokenType.COMMA, self.parse_variable))
            self.expect(TokenType.RIGHT_BRACKET)
        return grammar.Expression(
            location=location,
            source=dedent(value).strip(),
            free_variables=free_variables
        )

    def parse_variable(self) -> grammar.Variable:
        location = self.current.location
        identifier = self.expectv(TokenType.IDENTIFIER)
        return grammar.Variable(
            location=location,
            identifier=identifier
        )

    def parse_type(self) -> grammar.Type:
        location = self.current.location
        value = self.expectv(TokenType.EXTERNAL)[1:-1]
        return grammar.Type(
            location=location,
            source=value
        )

    def parse_program(self) -> grammar.Program:
        location = self.current.location
        self.expect(TokenType.CALL)
        main_function_name = self.parse_variable()
        self.expect(TokenType.LEFT_PAREN)
        if self.match(TokenType.RIGHT_PAREN):
            inputs = None
        else:
            inputs = self.parse_expression()
            self.expect(TokenType.RIGHT_PAREN)
        self.expect(TokenType.IN)
        function_list = [self.parse_function()]
        while not self.done:
            function_list.append(self.parse_function())
        return grammar.Program(
            location=location,
            main_function_name=main_function_name,
            inputs=inputs,
            function_list=function_list
        )

    def parse_function(self) -> grammar.Function:
        location = self.current.location
        self.expect(TokenType.FUN)
        name = self.parse_variable()
        self.expect(TokenType.LEFT_PAREN)
        if self.match(TokenType.RIGHT_PAREN):
            parameters = {}
        else:
            parameters = {
                variable: declaration.type
                for declaration in self.sequence(TokenType.COMMA, self.parse_declaration)
                for variable in declaration.variables
            }
            self.expect(TokenType.RIGHT_PAREN)
        self.expect(TokenType.RIGHT_ARROW)
        returns = [self.parse_type()]
        while self.match(TokenType.COMMA):
            returns.append(self.parse_type())
        self.expect(TokenType.COLON)
        body = self.parse_statement()

        return grammar.Function(
            location=location,
            name=name,
            parameters=parameters,
            returns=returns,
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
        elif self.lookahead(TokenType.RETURN):
            return self.parse_return()
        elif self.lookahead(TokenType.IDENTIFIER):
            return self.parse_variable_bunch()
        elif self.lookahead(TokenType.LEFT_BRACE):
            return self.parse_block()
        elif self.lookahead(TokenType.NOOP):
            return self.parse_noop()
        else:
            raise self.error("Expected statement.")

    def parse_loop(self) -> grammar.Loop:
        location = self.current.location
        self.expect(TokenType.LOOP)
        name = self.parse_variable()
        body = self.parse_statement()
        return grammar.Loop(
            location=location,
            name=name,
            body=body
        )

    def parse_continue(self) -> grammar.Continue:
        location = self.current.location
        self.expect(TokenType.CONTINUE)
        name = self.parse_variable()
        return grammar.Continue(
            location=location,
            name=name
        )

    def parse_break(self) -> grammar.Break:
        location = self.current.location
        self.expect(TokenType.BREAK)
        name = self.parse_variable()
        return grammar.Break(
            location=location,
            name=name
        )

    def parse_if(self) -> grammar.If:
        location = self.current.location
        self.expect(TokenType.IF)
        condition = self.parse_variable()
        self.expect(TokenType.THEN)
        truthy_branch = self.parse_statement()
        self.expect(TokenType.ELSE)
        falsey_branch = self.parse_statement()
        return grammar.If(
            location=location,
            condition=condition,
            truthy_branch=truthy_branch,
            falsey_branch=falsey_branch
        )

    def parse_return(self) -> grammar.Return:
        location = self.current.location
        self.expect(TokenType.RETURN)
        variables = [self.parse_variable()]
        while self.match(TokenType.COMMA):
            variables.append(self.parse_variable())
        return grammar.Return(
            location=location,
            variables=variables
        )

    def parse_variable_bunch(self) -> grammar.Declaration | grammar.Assignment | grammar.Call:
        location = self.current.location
        variables = [self.parse_variable()]
        while self.match(TokenType.COMMA):
            variables.append(self.parse_variable())
        if self.match(TokenType.LEFT_ARROW):
            expression = self.parse_expression()
            return grammar.Assignment(
                location=location,
                variables=variables,
                expression=expression
            )
        elif self.match(TokenType.DOUBLE_LEFT_ARROW):
            function = self.parse_variable()
            self.expect(TokenType.LEFT_PAREN)
            if self.match(TokenType.RIGHT_PAREN):
                arguments = []
            else:
                arguments = [self.parse_variable()]
                while self.match(TokenType.COMMA):
                    arguments.append(self.parse_variable())
                self.expect(TokenType.RIGHT_PAREN)
            return grammar.Call(
                location=location,
                variables=variables,
                function=function,
                arguments=arguments
            )
        elif self.match(TokenType.COLON):
            type = self.parse_type()
            return grammar.Declaration(
                location=location,
                variables=variables,
                type=type
            )
        else:
            raise self.error("Expected either LEFT_ARROW or COLON.")

    def parse_declaration(self) -> grammar.Declaration:
        location = self.current.location
        variables = [self.parse_variable()]
        while self.match(TokenType.COMMA):
            variables.append(self.parse_variable())
        self.expect(TokenType.COLON)
        type = self.parse_type()
        return grammar.Declaration(
            location=location,
            variables=variables,
            type=type
        )

    def parse_block(self) -> grammar.Block:
        location = self.current.location
        self.expect(TokenType.LEFT_BRACE)
        statements = [self.parse_statement()]
        while self.match(TokenType.SEMICOLON):
            statements.append(self.parse_statement())
        self.expect(TokenType.RIGHT_BRACE)
        return grammar.Block(
            location=location,
            statements=statements
        )

    def parse_noop(self) -> grammar.NoOp:
        location = self.current.location
        self.expect(TokenType.NOOP)
        return grammar.NoOp(
            location=location
        )
