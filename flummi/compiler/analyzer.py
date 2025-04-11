from dataclasses import dataclass, field, replace

from ..IR import AST, common

from ..library import errors
from . import parser

__all__ = (
    "analyze",
    "SymbolTable",
)


class AnalysisError(errors.PrettyError):
    ...


type SymbolTable[A] = dict[common.Identifier[A], common.Type[A]]


def analyze(program: parser.Program) -> tuple[parser.Program, SymbolTable[errors.Location]]:
    return Analyzer().analyze_program(program)


@dataclass
class Analyzer:
    functions      : dict[parser.Identifier, parser.Function] = field(init=False)

    symbol_table   : SymbolTable             = field(init=False, default_factory=dict)
    bound_symbols  : set[parser.Identifier]  = field(init=False, default_factory=set)

    loop_names     : set[parser.Identifier]        = field(init=False, default_factory=set)
    loop_scope     : list[parser.Identifier]       = field(init=False, default_factory=list)
    loop_broken    : dict[parser.Identifier, bool] = field(init=False, default_factory=dict)
    loop_stopped   : dict[parser.Identifier, bool] = field(init=False, default_factory=dict)

    variable_prefix: str = field(init=False, default_factory=str)

    called_functions: set[parser.Identifier] = field(init=False, default_factory=set)

    def analyze_program(
        self,
        program: parser.Program
    ) -> tuple[parser.Program, SymbolTable]:
        self.functions = program.functions

        for i, function in enumerate(program.function_list):
            function.parameters = {
                common.Identifier(
                    function.name.identifier + "." + parameter.identifier,
                    annotation=parameter.annotation
                ): type
                for parameter, type in function.parameters.items()
            }

            for other_function in program.function_list[i+1:]:
                if function.name.identifier == other_function.name.identifier:
                    raise AnalysisError(
                        "Found definition of function "
                        f"{other_function.name.identifier!r}",
                        other_function.annotation,
                        "",
                        "...that was already definied.",
                        function.annotation
                    )

        program.statement, stopped, _ = self.analyze_statement(program.statement)

        if not stopped:
            raise AnalysisError(
                "Not all linear control paths in the top level statement are "
                "termianted by a STOP statement.",
                program.statement.annotation
            )

        stack = list(self.called_functions)
        seen = set()
        analyzed_functions = []

        while stack:
            function = stack.pop()
            seen.add(function)
            self.called_functions = set()
            analyzed_functions.append(
                self.analyze_function(program.functions[function])
            )
            stack += list(self.called_functions - seen)

        program.function_list = analyzed_functions

        return program, self.symbol_table

    def analyze_function(self, function: parser.Function) -> parser.Function:
        self.variable_prefix = function.name.identifier + "."
        self.symbol_table.update(function.parameters)
        self.bound_symbols.update(function.parameters.keys())
        self.function_name = function.name

        function.body, stopped, _ = self.analyze_statement(function.body)

        if not stopped:
            raise AnalysisError(
                "Not all linear control paths in this function are termianted "
                "by a STOP statement.",
                function.annotation
            )

        return function

    def analyze_statement(
        self,
        statement: parser.Statement
    ) -> tuple[parser.Statement, bool, bool]:
        match statement:
            case AST.Block(statements):
                if not statements:
                    raise AnalysisError(
                        "Found empty block.",
                        statement.annotation
                    )

                new_statements = []
                for child_statement in statements:
                    new_child_statement, stopped, elide =\
                        self.analyze_statement(child_statement)
                    if not elide:
                        new_statements.append(new_child_statement)
                        if stopped:
                            break


                if len(new_statements) == 1:
                    return (
                        new_statements[0],
                        stopped,
                        False
                    )
                else:
                    return (
                        replace(statement, statements=new_statements),
                        stopped,
                        len(new_statements) == 0
                    )

            case AST.NoOp():
                return statement, False, True

            case AST.Declaration(variables, type):
                for variable in variables:
                    variable.identifier = self.variable_prefix + variable.identifier
                    if variable in self.symbol_table:
                        original_declaration = next(
                            _variable
                            for _variable in self.symbol_table
                            if _variable.identifier == variable.identifier
                        )
                        raise AnalysisError(
                            "Found declaration of variable "
                            f"{variable.identifier!r}...",
                            variable.annotation,
                            "",
                            "...that was already declared at.",
                            original_declaration.annotation
                        )
                    else:
                        self.symbol_table[variable] = type

                return statement, False, True

            case AST.Let(variable, expression):
                self.analyze_expression(expression)
                self.analyze_variable_write(variable)

                return statement, False, False

            case AST.Stop():
                for loop_label in self.loop_scope:
                    self.loop_stopped[loop_label] = True

                return statement, True, False

            case AST.Emit(variable):
                self.analyze_variable_read(variable)

                return statement, False, False

            case AST.If(condition, truthy_branch, falsey_branch):
                self.analyze_variable_read(condition)

                truthy_branch, truthy_stopped, elide_truthy =\
                    self.analyze_statement(truthy_branch)

                falsey_branch, falsey_stopped, elide_falsey =\
                    self.analyze_statement(falsey_branch)

                return (
                    replace(
                        statement,
                        truthy_branch=
                            AST.NoOp(annotation=truthy_branch.annotation)
                            if elide_truthy else truthy_branch,
                        falsey_branch=
                            AST.NoOp(annotation=falsey_branch.annotation)
                            if elide_falsey else falsey_branch
                    ),
                    truthy_stopped and falsey_stopped,
                    elide_truthy and elide_falsey
                )

            case AST.Loop(loop_label, body):
                if loop_label in self.loop_names:
                    original_introduction = next(
                        variable
                        for variable in self.loop_names
                        if variable.identifier == loop_label.identifier
                    )
                    raise AnalysisError(
                        "Found introduction of loop label "
                        f"{loop_label.identifier!r}...",
                        loop_label.annotation,
                        "",
                        "...that was already introduced at.",
                        original_introduction.annotation
                    )

                self.loop_names.add(loop_label)
                self.loop_scope.append(loop_label)
                self.loop_broken[loop_label] = False
                self.loop_stopped[loop_label] = False

                statement.body, _, elide_body =\
                    self.analyze_statement(body)

                self.loop_scope.append(loop_label)
                if (
                    not self.loop_stopped[loop_label] and
                    not self.loop_broken[loop_label]
                ):
                    raise AnalysisError(
                        "Found loop containing neither a STOP statement nor "
                        "a BREAK statement referencing either this loop or "
                        "any of its parent loops.",
                        statement.annotation
                    )

                return (
                    statement,
                    self.loop_stopped[loop_label],
                    elide_body
                )

            case AST.Break(loop_label):
                if loop_label not in self.loop_scope:
                    raise AnalysisError(
                        "Found break to unintroduced loop label "
                        f"{loop_label.identifier!r}.",
                        loop_label.annotation
                    )

                for _loop_label in self.loop_scope[::-1]:
                    self.loop_broken[_loop_label] = True
                    if loop_label == _loop_label:
                        break

                return statement, False, False

            case AST.Continue(loop_label):
                if loop_label not in self.loop_scope:
                    raise AnalysisError(
                        "Found continue to unintroduced loop label "
                        f"{loop_label.identifier!r}.",
                        loop_label.annotation
                    )

                return statement, False, False

            case AST.Call(function, arguments, variable):
                self.analyze_call_parameters(function, arguments)
                self.analyze_variable_write(variable)
                self.called_functions.add(function)

                return statement, False, False

            case AST.TailCall(function, arguments):
                self.analyze_call_parameters(function, arguments)
                self.called_functions.add(function)

                return statement, True, False

            case AST.Lookup(result, hit, function, arguments):
                self.analyze_call_parameters(function, arguments)
                self.analyze_variable_write(result)
                self.analyze_variable_write(hit)

                return statement, False, False

            case AST.Memoize(function, arguments, value):
                self.analyze_call_parameters(function, arguments)
                self.analyze_variable_read(value)

                return statement, False, False

            case _:
                raise AnalysisError(
                    "Found unknown statement.",
                    statement.annotation
                )

    def analyze_expression(self, expression: parser.Expression):
        for variable in expression.arguments:
            self.analyze_variable_read(variable)

    def analyze_call_parameters(self, function: parser.Identifier, arguments: dict[parser.Identifier, parser.Identifier]):
        if function not in self.functions:
            raise AnalysisError(
                "Found call to unknown function ",
                f"{function.identifier!r}.",
                function.annotation,
            )

        function_definition = self.functions[function]

        for parameter in arguments.keys():
            parameter.identifier = function.identifier + "." + parameter.identifier

        if arguments.keys() != function_definition.parameters.keys():
            raise AnalysisError(
                "Found mismatch between arguments...",
                list(arguments.values())[-1].annotation,
                "...and the expected parameters.",
                function.annotation,
                str(function_definition.parameters)
            )
        for argument in arguments.values():
            self.analyze_variable_read(argument)

    def analyze_variable_read(self, variable: parser.Identifier):
        variable.identifier = self.variable_prefix + variable.identifier
        if variable not in self.bound_symbols:
            raise AnalysisError(
                "Found read from uninitialised variable "
                f"{variable.identifier!r}.",
                variable.annotation
            )

    def analyze_variable_write(self, variable: parser.Identifier):
        variable.identifier = self.variable_prefix + variable.identifier
        if variable not in self.bound_symbols:
            if variable not in self.symbol_table:
                raise AnalysisError(
                    "Found write to undeclared variable "
                    f"{variable.identifier!r}.",
                    variable.annotation
                )
        self.bound_symbols.add(variable)
