from textwrap import dedent

from ..IR import AST, common

from ..library import errors, parser


__all__ = ("parse",)

type Annotation = errors.Location
type Program = AST.Program[Annotation]
type Statement = AST.Statement[Annotation]
type Block = AST.Block[Annotation]
type NoOp = AST.NoOp[Annotation]
type Emit = AST.Emit[Annotation]
type Stop = AST.Stop[Annotation]
type Let = AST.Let[Annotation]
type Expression = common.Expression[Annotation]
type Type = common.Type[Annotation]
type Identifier = common.Identifier[Annotation]


class ParserError(errors.PrettyError): ...


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
        return common.Expression(
            annotation=location,
            source=dedent(value).strip(),
            arguments=free_variables,
        )

    def parse_variable(self) -> Identifier:
        location = self.current.location
        identifier = self.expectv(Tokens.IDENTIFIER)
        return common.Identifier(annotation=location, identifier=identifier)

    def parse_type(self) -> Type:
        location = self.current.location
        value = self.expectv(Tokens.SQL)[1:-1]
        return common.Type(annotation=location, source=value)

    def parse_program(self) -> Program:
        location = self.current.location
        body = self.parse_statement()
        return common.Program(annotation=location, body=body)

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
        else:
            raise self.error("Expected statement.")

    def parse_stop(self) -> Stop:
        location = self.current.location
        self.expect(Tokens.STOP)
        return AST.Stop(annotation=location)

    def parse_emit(self) -> Emit:
        location = self.current.location
        self.expect(Tokens.EMIT)
        variable = self.parse_variable()
        return AST.Emit(annotation=location, variable=variable)

    def parse_block(self) -> Block:
        location = self.current.location
        self.expect(Tokens.LEFT_BRACE)
        statements = list(self.sequence(self.parse_statement, Tokens.SEMICOLON))
        self.expect(Tokens.RIGHT_BRACE)
        return AST.Block(annotation=location, statements=statements)

    def parse_noop(self) -> NoOp:
        location = self.current.location
        self.expect(Tokens.NOOP)
        return AST.NoOp(annotation=location)

    def parse_let(self) -> Let:
        location = self.current.location
        self.expect(Tokens.LET)
        variable = self.parse_variable()
        self.expect(Tokens.EQUALS)
        expression = self.parse_expression()
        return AST.Let(
            annotation=location, variable=variable, expression=expression
        )
