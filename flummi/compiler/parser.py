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
type NoOp        = AST.NoOp[errors.Location]
type Return      = AST.Return[errors.Location]
type If          = AST.If[errors.Location]
type Let         = AST.Let[errors.Location]
type TailCall    = AST.TailCall[errors.Location]
type Call        = AST.Call[errors.Location]
type Lookup      = AST.Lookup[errors.Location]
type Memoize     = AST.Memoize[errors.Location]
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
    TAIL = r"TAIL"
    CALL = r"CALL"
    IN = r"IN"
    AS = r"AS"
    FUN = r"FUN"
    LET = r"LET"
    DECLARE = r"DECLARE"
    LOOP = r"LOOP"
    CONTINUE = r"CONTINUE"
    BREAK = r"BREAK"
    RETURN = r"RETURN"
    THEN = r"THEN"
    ELSE = r"ELSE"
    NOOP = r"NOOP"
    LOOKUP = r"LOOKUP"
    MEMOIZE = r"MEMOIZE"
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
        statement = self.parse_statement()
        function_list = []
        while not self.done:
            function_list.append(self.parse_function())
        return common.Program(
            annotation=location,
            statement=statement,
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
                for variable, type in self.sequence(
                    lambda: (
                        self.parse_variable(),
                        self.expect(Tokens.COLON) or
                        self.parse_type()
                    ),
                    Tokens.COMMA
                )
            }
            self.expect(Tokens.RIGHT_PAREN)
        self.expect(Tokens.RIGHT_ARROW)
        return_type = self.parse_type()
        self.expect(Tokens.COLON)
        body = self.parse_statement()

        return common.Function(
            annotation=location,
            name=name,
            parameters=parameters,
            return_type=return_type,
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
        elif self.lookahead(Tokens.RETURN):
            return self.parse_return()
        elif self.lookahead(Tokens.LEFT_BRACE):
            return self.parse_block()
        elif self.lookahead(Tokens.NOOP):
            return self.parse_noop()
        elif self.lookahead(Tokens.LET):
            return self.parse_let()
        elif self.lookahead(Tokens.DECLARE):
            return self.parse_declaration()
        elif self.lookahead(Tokens.TAIL):
            return self.parse_tail_call()
        elif self.lookahead(Tokens.CALL):
            return self.parse_call()
        elif self.lookahead(Tokens.LOOKUP):
            return self.parse_lookup()
        elif self.lookahead(Tokens.MEMOIZE):
            return self.parse_memoize()
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

    def parse_return(self) -> Return:
        location = self.current.location
        self.expect(Tokens.RETURN)
        variable = self.parse_variable()
        return AST.Return(
            annotation=location,
            variable=variable
        )

    def parse_block(self) -> Block:
        location = self.current.location
        self.expect(Tokens.LEFT_BRACE)
        statements = list(self.sequence(self.parse_statement, Tokens.SEMICOLON))
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

    def parse_let(self) -> Let:
        location = self.current.location
        self.expect(Tokens.LET)
        variable = self.parse_variable()
        self.expect(Tokens.EQUALS)
        expression = self.parse_expression()
        return AST.Let(
            annotation=location,
            variable=variable,
            expression=expression
        )

    def parse_declaration(self) -> Declaration:
        location = self.current.location
        self.expect(Tokens.DECLARE)
        variables = list(self.sequence(self.parse_variable, Tokens.COMMA))
        self.expect(Tokens.COLON)
        type = self.parse_type()
        return AST.Declaration(
            annotation=location,
            variables=variables,
            type=type
        )

    def parse_argument(self) -> tuple[Identifier, Identifier]:
        parameter = self.parse_variable()
        self.expect(Tokens.COLON)
        argument = self.parse_variable()
        return parameter, argument

    def parse_tail_call(self) ->TailCall:
        location = self.current.location
        self.expect(Tokens.TAIL)
        function = self.parse_variable()
        self.expect(Tokens.LEFT_PAREN)
        arguments = dict(self.sequence(self.parse_argument, Tokens.COMMA))
        self.expect(Tokens.RIGHT_PAREN)
        return AST.TailCall(
            annotation=location,
            function=function,
            arguments=arguments,
        )

    def parse_call(self) -> Call:
        location = self.current.location
        self.expect(Tokens.CALL)
        variable = self.parse_variable()
        self.expect(Tokens.EQUALS)
        function = self.parse_variable()
        self.expect(Tokens.LEFT_PAREN)
        arguments = dict(self.sequence(self.parse_argument, Tokens.COMMA))
        self.expect(Tokens.RIGHT_PAREN)
        return AST.Call(
            annotation=location,
            variable=variable,
            function=function,
            arguments=arguments,
        )

    def parse_lookup(self) -> Lookup:
        location = self.current.location
        self.expect(Tokens.LOOKUP)
        result = self.parse_variable()
        self.expect(Tokens.COMMA)
        hit = self.parse_variable()
        self.expect(Tokens.EQUALS)
        function = self.parse_variable()
        self.expect(Tokens.LEFT_PAREN)
        arguments = dict(self.sequence(self.parse_argument, Tokens.COMMA))
        self.expect(Tokens.RIGHT_PAREN)
        return AST.Lookup(
            annotation=location,
            result=result,
            hit=hit,
            function=function,
            arguments=arguments,
        )

    def parse_memoize(self) -> Memoize:
        location = self.current.location
        self.expect(Tokens.MEMOIZE)
        function = self.parse_variable()
        self.expect(Tokens.LEFT_PAREN)
        arguments = dict(self.sequence(self.parse_argument, Tokens.COMMA))
        self.expect(Tokens.RIGHT_PAREN)
        self.expect(Tokens.EQUALS)
        variable = self.parse_variable()
        return AST.Memoize(
            annotation=location,
            function=function,
            arguments=arguments,
            value=variable,
        )
