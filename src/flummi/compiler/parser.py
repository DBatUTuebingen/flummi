from textwrap import dedent

from ..IR.AST import (
    Assignment,
    Block,
    Break,
    Conditional,
    Continue,
    Declaration,
    Emit,
    Loop,
    NoOp,
    Program,
    Statement,
    Stop,
)
from ..IR.common import (
    Expression,
    Label,
    Type,
    Variable,
)
from ..library import errors, parser

__all__ = ("parse",)


class ParserError(errors.PrettyError, SyntaxError): ...


def parse(source: str) -> Program:
    return Parser(source, lex).parse_program()


class Tokens(parser.Tokens):
    LEFT_BRACE = r"{"
    LEFT_BRACKET = r"\["
    RIGHT_BRACE = r"}"
    RIGHT_BRACKET = r"\]"
    SEMICOLON = r";"
    COMMA = r","
    SQL = r"[§][^§]+[§]"
    EQUALS = r"="
    LET = r"LET"
    EMIT = r"EMIT"
    STOP = r"STOP"
    NOOP = r"NOOP"
    IF = r"IF"
    THEN = r"THEN"
    ELSE = r"ELSE"
    DECLARE = r"DECLARE"
    COLON = r":"
    LOOP = r"LOOP"
    CONTINUE = r"CONTINUE"
    BREAK = r"BREAK"
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
                self.sequence(self.parse_variable, Tokens.COMMA)
            )
            self.expect(Tokens.RIGHT_BRACKET)
        return Expression(
            location=location,
            source=dedent(value).strip(),
            arguments=free_variables,
        )

    def parse_variable(self) -> Variable:
        location = self.current.location
        identifier = self.expectv(Tokens.IDENTIFIER)
        return Variable(location=location, identifier=identifier)

    def parse_label(self) -> Label:
        location = self.current.location
        identifier = self.expectv(Tokens.IDENTIFIER)
        return Label(location=location, identifier=identifier)

    def parse_type(self) -> Type:
        location = self.current.location
        value = self.expectv(Tokens.SQL)[1:-1]
        return Type(location=location, source=value)

    def parse_program(self) -> Program:
        location = self.current.location
        body = self.parse_statement()
        return Program(location=location, body=body)

    def parse_statement(self) -> Statement:
        if self.lookahead(Tokens.DECLARE):
            return self.parse_declaration()
        if self.lookahead(Tokens.STOP):
            return self.parse_stop()
        elif self.lookahead(Tokens.EMIT):
            return self.parse_emit()
        elif self.lookahead(Tokens.LEFT_BRACE):
            return self.parse_block()
        elif self.lookahead(Tokens.NOOP):
            return self.parse_noop()
        elif self.lookahead(Tokens.LET):
            return self.parse_assignment()
        elif self.lookahead(Tokens.IF):
            return self.parse_conditional()
        elif self.lookahead(Tokens.LOOP):
            return self.parse_loop()
        elif self.lookahead(Tokens.CONTINUE):
            return self.parse_continue()
        elif self.lookahead(Tokens.BREAK):
            return self.parse_break()
        else:
            raise self.error("Expected statement.")

    def parse_declaration(self) -> Declaration:
        location = self.current.location
        self.expect(Tokens.DECLARE)
        variable = self.parse_variable()
        self.expect(Tokens.COLON)
        type = self.parse_type()
        return Declaration(
            location=location,
            variable=variable,
            type=type,
        )

    def parse_stop(self) -> Stop:
        location = self.current.location
        self.expect(Tokens.STOP)
        return Stop(location=location)

    def parse_emit(self) -> Emit:
        location = self.current.location
        self.expect(Tokens.EMIT)
        variable = self.parse_variable()
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

    def parse_assignment(self) -> Assignment:
        location = self.current.location
        self.expect(Tokens.LET)
        variable = self.parse_variable()
        self.expect(Tokens.EQUALS)
        expression = self.parse_expression()
        return Assignment(
            location=location, variable=variable, expression=expression
        )

    def parse_conditional(self) -> Conditional:
        location = self.current.location
        self.expect(Tokens.IF)
        condition = self.parse_variable()
        self.expect(Tokens.THEN)
        true_branch = self.parse_statement()
        self.expect(Tokens.ELSE)
        false_branch = self.parse_statement()
        return Conditional(
            location=location,
            condition=condition,
            true_branch=true_branch,
            false_branch=false_branch,
        )

    def parse_loop(self) -> Loop:
        location = self.current.location
        self.expect(Tokens.LOOP)
        label = self.parse_label()
        body = self.parse_statement()
        return Loop(
            location=location,
            label=label,
            body=body,
        )

    def parse_continue(self) -> Continue:
        location = self.current.location
        self.expect(Tokens.CONTINUE)
        label = self.parse_label()
        return Continue(
            location=location,
            label=label,
        )

    def parse_break(self) -> Break:
        location = self.current.location
        self.expect(Tokens.BREAK)
        label = self.parse_label()
        return Break(
            location=location,
            label=label,
        )
