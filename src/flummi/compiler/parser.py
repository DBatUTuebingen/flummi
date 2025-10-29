from textwrap import dedent

from ..IR.common import Expression, Type, Identifier
from ..IR.AST import (
    Program,
    Statement,
    Variable,
    Block,
    Declare,
    Let,
    Emit,
    Stop,
    NoOp,
    If,
    Loop,
    Continue,
    Break,
    Fork,
    Gather,
    Sync,
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
    LOOP = r"LOOP"
    CONTINUE = r"CONTINUE"
    BREAK = r"BREAK"
    FORK = r"FORK"
    GATHER = r"GATHER"
    BY = r"BY"
    SYNC = r"SYNC"
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
        elif self.lookahead(Tokens.LOOP):
            return self.parse_loop()
        elif self.lookahead(Tokens.CONTINUE):
            return self.parse_continue()
        elif self.lookahead(Tokens.BREAK):
            return self.parse_break()
        elif self.lookahead(Tokens.FORK):
            return self.parse_fork()
        elif self.lookahead(Tokens.GATHER):
            return self.parse_gather()
        elif self.lookahead(Tokens.SYNC):
            return self.parse_sync()
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

    def parse_loop(self) -> Loop:
        location = self.current.location
        self.expect(Tokens.LOOP)
        name = self.parse_identifier()
        body = self.parse_statement()
        return Loop(location=location, name=name, body=body)

    def parse_continue(self) -> Continue:
        location = self.current.location
        self.expect(Tokens.CONTINUE)
        name = self.parse_identifier()
        return Continue(
            location=location,
            name=name,
        )

    def parse_break(self) -> Break:
        location = self.current.location
        self.expect(Tokens.BREAK)
        name = self.parse_identifier()
        return Break(
            location=location,
            name=name,
        )

    def parse_fork(self) -> Fork:
        location = self.current.location
        self.expect(Tokens.FORK)
        variables = list(self.sequence(self.parse_identifier, Tokens.COMMA))
        self.expect(Tokens.EQUALS)
        expression = self.parse_expression()
        return Fork(
            variables=variables, expression=expression, location=location
        )

    def parse_gather(self) -> Gather:
        location = self.current.location
        self.expect(Tokens.GATHER)

        def parse_aggregate() -> tuple[Variable, Expression]:
            variable = self.parse_identifier()
            self.expect(Tokens.EQUALS)
            expression = self.parse_expression()
            return variable, expression

        aggregates = dict(self.sequence(parse_aggregate, Tokens.COMMA))

        if self.match(Tokens.BY):
            keys = list(self.sequence(self.parse_identifier, Tokens.COMMA))
        else:
            keys = []

        return Gather(aggregates=aggregates, keys=keys, location=location)

    def parse_sync(self) -> Sync:
        location = self.current.location
        self.expect(Tokens.SYNC)
        if self.match(Tokens.BY):
            keys = list(self.sequence(self.parse_identifier, Tokens.COMMA))
        else:
            keys = []
        return Sync(keys, location=location)
