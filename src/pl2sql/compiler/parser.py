from textwrap import dedent

from ..IR.common import Expression, Type, Identifier
from ..IR.AST import (
    Program,
    Statement,
    Block,
    Declare,
    Let,
    Emit,
    Stop,
    NoOp,
    If,
)

from ..library import errors, parser


__all__ = ("parse",)


class ParserError(errors.PrettyError): ...


def parse(source: str) -> Program:
    return Parser(source, lex).parse_program()


class Tokens(parser.Tokens):
    LEFT_BRACE = r"{"
    LEFT_BRACKET = r"\["
    RIGHT_BRACE = r"}"
    RIGHT_BRACKET = r"\]"
    COLON = r":"
    SEMICOLON = r";"
    COMMA = r","
    SQL = r"[§][^§]+[§]"
    EQUALS = r"="
    DECLARE = r"DECLARE"
    LET = r"LET"
    EMIT = r"EMIT"
    STOP = r"STOP"
    NOOP = r"NOOP"
    IF = r"IF"
    THEN = r"THEN"
    ELSE = r"ELSE"
    IDENTIFIER = r"\w+"
    COMMENT = r"--[^\n]*"
    WHITESPACE = r"\s+"


lex = parser.make_lexer(Tokens, {Tokens.WHITESPACE, Tokens.COMMENT})


class Parser(parser.Parser[Tokens]):
    def parse_expression(self) -> Expression:
        location = self.current.location
        value = self.expectv(Tokens.SQL)[1:-1]
        self.expect(Tokens.LEFT_BRACKET)
        if self.match(Tokens.RIGHT_BRACKET):
            free_variables = []
        else:
            free_variables = list(
                self.sequence(self.parse_identifier, Tokens.COMMA)
            )
            self.expect(Tokens.RIGHT_BRACKET)
        return Expression(
            location=location,
            source=dedent(value).strip(),
            arguments=free_variables,
        )

    def parse_identifier(self) -> Identifier:
        location = self.current.location
        identifier = self.expectv(Tokens.IDENTIFIER)
        return Identifier(location=location, identifier=identifier)

    def parse_type(self) -> Type:
        location = self.current.location
        value = self.expectv(Tokens.SQL)[1:-1]
        return Type(location=location, source=value)

    def parse_program(self) -> Program:
        location = self.current.location
        body = self.parse_statement()
        return Program(location=location, body=body)

    def parse_statement(self) -> Statement:
        if self.lookahead(Tokens.STOP):
            return self.parse_stop()
        elif self.lookahead(Tokens.EMIT):
            return self.parse_emit()
        elif self.lookahead(Tokens.LEFT_BRACE):
            return self.parse_block()
        elif self.lookahead(Tokens.NOOP):
            return self.parse_noop()
        elif self.lookahead(Tokens.LET):
            return self.parse_let()
        elif self.lookahead(Tokens.IF):
            return self.parse_if()
        elif self.lookahead(Tokens.DECLARE):
            return self.parse_declare()
        else:
            raise self.error("Expected statement.")

    def parse_stop(self) -> Stop:
        location = self.current.location
        self.expect(Tokens.STOP)
        return Stop(location=location)

    def parse_emit(self) -> Emit:
        location = self.current.location
        self.expect(Tokens.EMIT)
        variable = self.parse_identifier()
        return Emit(location=location, variable=variable)

    def parse_block(self) -> Block:
        location = self.current.location
        self.expect(Tokens.LEFT_BRACE)
        statements = list(self.sequence(self.parse_statement, Tokens.SEMICOLON))
        self.expect(Tokens.RIGHT_BRACE)
        return Block(location=location, statements=statements)

    def parse_noop(self) -> NoOp:
        location = self.current.location
        self.expect(Tokens.NOOP)
        return NoOp(location=location)

    def parse_let(self) -> Let:
        location = self.current.location
        self.expect(Tokens.LET)
        variable = self.parse_identifier()
        self.expect(Tokens.EQUALS)
        expression = self.parse_expression()
        return Let(location=location, variable=variable, expression=expression)

    def parse_if(self) -> If:
        location = self.current.location
        self.expect(Tokens.IF)
        variable = self.parse_identifier()
        self.expect(Tokens.THEN)
        truthy_branch = self.parse_statement()
        self.expect(Tokens.ELSE)
        falsey_branch = self.parse_statement()
        return If(
            location=location,
            condition=variable,
            truthy_branch=truthy_branch,
            falsey_branch=falsey_branch,
        )

    def parse_declare(self) -> Declare:
        location = self.current.location
        self.expect(Tokens.DECLARE)
        variable = self.parse_identifier()
        self.expect(Tokens.COLON)
        type = self.parse_type()
        return Declare(location=location, variable=variable, type=type)
