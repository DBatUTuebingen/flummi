from enum import StrEnum, unique
from textwrap import dedent

from ..IR import AST, common

from ..library import errors, parser


__all__ = (
    "parse",
)


type Program     = AST.Program[errors.Location]
type Function    = AST.Function[errors.Location]
type Statement   = AST.Statement[errors.Location]
type Loop        = AST.Loop[errors.Location]
type Break       = AST.Break[errors.Location]
type Continue    = AST.Continue[errors.Location]
type Block       = AST.Block[errors.Location]
type Emit        = AST.Emit[errors.Location]
type Stop        = AST.Stop[errors.Location]
type If          = AST.If[errors.Location]
type Assignment  = AST.Assignment[errors.Location]
type Sync        = AST.Sync[errors.Location]
type Fork        = AST.Fork[errors.Location]
type Join        = AST.Join[errors.Location]
type NoOp        = AST.NoOp[errors.Location]
type Declaration = AST.Declaration[errors.Location]
type Expression  = common.Expression[errors.Location]
type Type        = common.Type[errors.Location]
type Identifier  = common.Identifier[errors.Location]


class ParserError(errors.PrettyError):
    ...


def parse(source: str) -> AST.Program[errors.Location]:
    return Parser(source, lex).parse_program()


class Tokens(parser.Tokens):
    LEFT_PAREN = r"\("
    LEFT_BRACE = r"{"
    LEFT_BRACKET = r"\["
    RIGHT_PAREN = r"\)"
    RIGHT_BRACE = r"}"
    RIGHT_BRACKET = r"\]"
    RIGHT_ARROW = r"->"
    COLON = r":"
    SEMICOLON = r";"
    COMMA = r","
    SQL = r"[§][^§]+[§]"
    EQUALS = r"="
    IF = r"IF"
    CALL = r"CALL"
    IN = r"IN"
    AS = r"AS"
    FUN = r"FUN"
    LET = r"LET"
    DECLARE = r"DECLARE"
    LOOP = r"LOOP"
    CONTINUE = r"CONTINUE"
    BREAK = r"BREAK"
    STOP = r"STOP"
    THEN = r"THEN"
    ELSE = r"ELSE"
    EMIT = r"EMIT"
    NOOP = r"NOOP"
    SYNC = r"SYNC"
    FORK = r"FORK"
    JOIN = r"JOIN"
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
            free_variables = list(self.sequence(self.parse_variable, Tokens.COMMA))
            self.expect(Tokens.RIGHT_BRACKET)
        return common.Expression(
            annotation=location,
            source=dedent(value).strip(),
            arguments=free_variables
        )

    def parse_variable(self) -> Identifier:
        location = self.current.location
        identifier = self.expectv(Tokens.IDENTIFIER)
        return common.Identifier(
            annotation=location,
            identifier=identifier
        )

    def parse_type(self) -> Type:
        location = self.current.location
        value = self.expectv(Tokens.SQL)[1:-1]
        return common.Type(
            annotation=location,
            source=value
        )

    def parse_program(self) -> Program:
        location = self.current.location
        self.expect(Tokens.CALL)
        main_function_name = self.parse_variable()
        self.expect(Tokens.LEFT_PAREN)
        if self.match(Tokens.RIGHT_PAREN):
            inputs = None
        else:
            inputs = self.parse_expression()
            self.expect(Tokens.RIGHT_PAREN)
        self.expect(Tokens.IN)
        function_list = [self.parse_function()]
        while not self.done:
            function_list.append(self.parse_function())
        return common.Program(
            annotation=location,
            main_function_name=main_function_name,
            inputs=inputs,
            function_list=function_list
        )

    def parse_function(self) -> Function:
        location = self.current.location
        self.expect(Tokens.FUN)
        name = self.parse_variable()
        self.expect(Tokens.LEFT_PAREN)
        if self.match(Tokens.RIGHT_PAREN):
            parameters = {}
        else:
            parameters = {
                variable: type
                for variables, type in self.sequence(
                    lambda: (
                        tuple(self.sequence(
                            self.parse_variable,
                            Tokens.COMMA
                        )),
                        self.expect(Tokens.COLON) or
                        self.parse_type()
                    ),
                    Tokens.COMMA
                )
                for variable in variables
            }
            self.expect(Tokens.RIGHT_PAREN)
        self.expect(Tokens.RIGHT_ARROW)
        returns = [self.parse_type()]
        while self.match(Tokens.COMMA):
            returns.append(self.parse_type())
        self.expect(Tokens.COLON)
        body = self.parse_statement()

        return common.Function(
            annotation=location,
            name=name,
            parameters=parameters,
            return_types=returns,
            body=body
        )

    def parse_statement(self) -> Statement:
        if self.lookahead(Tokens.LOOP):
            return self.parse_loop()
        elif self.lookahead(Tokens.CONTINUE):
            return self.parse_continue()
        elif self.lookahead(Tokens.BREAK):
            return self.parse_break()
        elif self.lookahead(Tokens.IF):
            return self.parse_if()
        elif self.lookahead(Tokens.EMIT):
            return self.parse_emit()
        elif self.lookahead(Tokens.LEFT_BRACE):
            return self.parse_block()
        elif self.lookahead(Tokens.NOOP):
            return self.parse_noop()
        elif self.lookahead(Tokens.STOP):
            return self.parse_stop()
        elif self.lookahead(Tokens.SYNC):
            return self.parse_sync()
        elif self.lookahead(Tokens.LET):
            return self.parse_assignment()
        elif self.lookahead(Tokens.DECLARE):
            return self.parse_declaration()
        elif self.lookahead(Tokens.FORK):
            return self.parse_fork()
        elif self.lookahead(Tokens.JOIN):
            return self.parse_join()
        else:
            raise self.error("Expected statement.")

    def parse_loop(self) -> Loop:
        location = self.current.location
        self.expect(Tokens.LOOP)
        name = self.parse_variable()
        body = self.parse_statement()
        return AST.Loop(
            annotation=location,
            name=name,
            body=body
        )

    def parse_continue(self) -> Continue:
        location = self.current.location
        self.expect(Tokens.CONTINUE)
        name = self.parse_variable()
        return AST.Continue(
            annotation=location,
            name=name
        )

    def parse_break(self) -> Break:
        location = self.current.location
        self.expect(Tokens.BREAK)
        name = self.parse_variable()
        return AST.Break(
            annotation=location,
            name=name
        )

    def parse_if(self) -> If:
        location = self.current.location
        self.expect(Tokens.IF)
        condition = self.parse_variable()
        self.expect(Tokens.THEN)
        truthy_branch = self.parse_statement()
        self.expect(Tokens.ELSE)
        falsey_branch = self.parse_statement()
        return AST.If(
            annotation=location,
            condition=condition,
            truthy_branch=truthy_branch,
            falsey_branch=falsey_branch
        )

    def parse_emit(self) -> Emit:
        location = self.current.location
        self.expect(Tokens.EMIT)
        variables = list(self.sequence(self.parse_variable, Tokens.COMMA))
        return AST.Emit(
            annotation=location,
            variables=variables
        )

    def parse_block(self) -> Block:
        location = self.current.location
        self.expect(Tokens.LEFT_BRACE)
        statements = [self.parse_statement()]
        while self.match(Tokens.SEMICOLON):
            statements.append(self.parse_statement())
        self.expect(Tokens.RIGHT_BRACE)
        return AST.Block(
            annotation=location,
            statements=statements
        )

    def parse_noop(self) -> NoOp:
        location = self.current.location
        self.expect(Tokens.NOOP)
        return AST.NoOp(
            annotation=location
        )

    def parse_stop(self) -> Stop:
        location = self.current.location
        self.expect(Tokens.STOP)
        return AST.Stop(
            annotation=location
        )

    def parse_sync(self) -> Sync:
        location = self.current.location
        self.expect(Tokens.SYNC)
        return AST.Sync(
            annotation=location
        )

    def parse_assignment(self) -> Assignment:
        location = self.current.location
        self.expect(Tokens.LET)
        variables = [self.parse_variable()]
        while self.match(Tokens.COMMA):
            variables.append(self.parse_variable())
        self.expect(Tokens.EQUALS)
        expression = self.parse_expression()
        return AST.Assignment(
            annotation=location,
            variables=variables,
            expression=expression
        )

    def parse_declaration(self) -> Declaration:
        location = self.current.location
        self.expect(Tokens.DECLARE)
        variables = [self.parse_variable()]
        while self.match(Tokens.COMMA):
            variables.append(self.parse_variable())
        self.expect(Tokens.COLON)
        type = self.parse_type()
        return AST.Declaration(
            annotation=location,
            variables=variables,
            type=type
        )

    def parse_fork(self) -> Fork:
        location = self.current.location
        self.expect(Tokens.FORK)
        variables = [self.parse_variable()]
        while self.match(Tokens.COMMA):
            variables.append(self.parse_variable())
        self.expect(Tokens.EQUALS)
        expression = self.parse_expression()
        return AST.Fork(
            annotation=location,
            variables=variables,
            expression=expression
        )

    def parse_join(self) -> Join:
        location = self.current.location
        self.expect(Tokens.JOIN)
        variables = [self.parse_variable()]
        while self.match(Tokens.COMMA):
            variables.append(self.parse_variable())
        self.expect(Tokens.EQUALS)
        expression = self.parse_expression()
        return AST.Join(
            annotation=location,
            variables=variables,
            expression=expression
        )
