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


def analyze(
    program: parser.Program
) -> tuple[parser.Program, dict[common.Identifier, SymbolTable[errors.Location]]]:
    for i, function in enumerate(program.function_list):
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

    if (
        program.inputs is not None and
        len(program.main_function.parameters) == 0
    ):
        raise AnalysisError(
            "Program supplies an input expression...",
            program.inputs.annotation,
            "",
            "...but the defined function did not expect one.",
            next(iter(program.main_function.parameters)).annotation
        )

    symbol_tables: dict[common.Identifier, SymbolTable] = {}
    for i, function in enumerate(program.function_list):
        program.function_list[i], symbol_table =\
            Analyzer(program).analyze(function)
        symbol_tables[function.name] = symbol_table

    return program, symbol_tables


@dataclass
class Analyzer:
    program          : AST.Program

    function_name    : parser.Identifier = field(init=False)

    symbol_table     : SymbolTable             = field(init=False, default_factory=dict)
    bound_symbols    : set[parser.Identifier]  = field(init=False, default_factory=set)

    loop_names       : set[parser.Identifier]        = field(init=False, default_factory=set)
    loop_scope       : list[parser.Identifier]       = field(init=False, default_factory=list)
    loop_broken      : dict[parser.Identifier, bool] = field(init=False, default_factory=dict)
    loop_stopped     : dict[parser.Identifier, bool] = field(init=False, default_factory=dict)

    def analyze(
        self,
        function: AST.Function
    ) -> tuple[AST.Function, SymbolTable]:
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

        return function, self.symbol_table

    def analyze_statement(
        self,
        statement: AST.Statement
    ) -> tuple[AST.Statement, bool, bool]:
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

            case AST.Assignment(variables, expression) | AST.Fork(variables, expression) | AST.Join(variables, expression):
                self.analyze_expression(expression)

                for variable in variables:
                    self.analyze_variable_write(variable)

                return statement, False, False

            case AST.Emit(variables):
                function = self.program.functions[self.function_name]
                delta = len(function.return_types)- len(variables)
                if delta != 0:
                    raise AnalysisError(
                        f"Found {["less", "more"][delta > 0]} "
                        "returned values...",
                        statement.annotation,
                        "",
                        "...than expected.",
                        function.annotation
                    )

                for variable in variables:
                    self.analyze_variable_read(variable)

                return statement, False, False

            case AST.Stop():
                for loop_label in self.loop_scope:
                    self.loop_stopped[loop_label] = True

                return statement, True, False

            case AST.Sync():
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

            case AST.Call(variables, function, arguments):
                if function not in self.program.functions:
                    raise AnalysisError(
                        "Found call to unknown function ",
                        f"{function.identifier!r}.",
                        function.annotation,
                    )

                function = self.program.functions[function]

                if len(arguments) != len(function.parameters):
                    raise AnalysisError(
                        "Found mismatch between number of arguments...",
                        arguments[-1].annotation,
                        "...and the number expected.",
                        function.annotation
                    )
                for argument in arguments:
                    self.analyze_variable_read(argument)

                if len(variables) != len(function.return_types):
                    raise AnalysisError(
                        "Found mismatch between number of bound variables...",
                        variables[-1].annotation,
                        "...and the number expected.",
                        function.return_types[-1].annotation
                    )
                for variable in variables:
                    self.analyze_variable_write(variable)

                return statement, False, False

            case _:
                raise AnalysisError(
                    "Found unknown statement.",
                    statement.annotation
                )

    def analyze_expression(self, expression: parser.Expression):
        for variable in expression.arguments:
            self.analyze_variable_read(variable)

    def analyze_variable_read(self, variable: parser.Identifier):
        if variable not in self.bound_symbols:
            raise AnalysisError(
                "Found read from uninitialised variable "
                f"{variable.identifier!r}.",
                variable.annotation
            )

    def analyze_variable_write(self, variable: parser.Identifier):
        if variable not in self.bound_symbols:
            if variable not in self.symbol_table:
                raise AnalysisError(
                    "Found write to undeclared variable "
                    f"{variable.identifier!r}.",
                    variable.annotation
                )
        self.bound_symbols.add(variable)
