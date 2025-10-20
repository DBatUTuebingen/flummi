from dataclasses import dataclass, field

from ..IR import AST, common

from ..library import errors

__all__ = ("analyze", "SymbolTable")


type SymbolTable = dict[common.Identifier, common.Type]


class AnalysisError(errors.PrettyError): ...


def analyze(
    program: AST.Program,
) -> tuple[AST.Program, SymbolTable]:
    analyzer = Analyzer()
    analyzed_program = analyzer.analyze_program(program)
    symbol_table = analyzer.symbol_table

    return analyzed_program, symbol_table


@dataclass
class Analyzer:
    symbol_table: SymbolTable = field(init=False, default_factory=dict)
    bound_symbols: set[common.Identifier] = field(
        init=False, default_factory=set
    )

    def analyze_program(self, program: AST.Program) -> AST.Program:
        result, stopped, _ = self.analyze_statement(program.body)

        if not stopped:
            raise AnalysisError(
                "Not all linear control paths in the top level statement are termianted by a STOP statement.",
                result.location,
            )

        program.body = result

        return program

    def analyze_statement(
        self, statement: AST.Statement
    ) -> tuple[AST.Statement, bool, bool]:
        match statement:
            case AST.Block(statements):
                if not statements:
                    raise AnalysisError(
                        "Found empty block.", statement.location
                    )

                stopped = True

                new_statements: list[AST.Statement] = []
                for child_statement in statements:
                    child_statement, child_stopped, child_elidable = (
                        self.analyze_statement(child_statement)
                    )
                    if not child_elidable:
                        new_statements.append(child_statement)
                        if child_stopped:
                            break
                else:
                    stopped = False

                if len(new_statements) == 0:
                    return AST.NoOp(location=statement.location), False, True
                elif len(new_statements) == 1:
                    return new_statements[0], stopped, False
                else:
                    statement.statements = new_statements
                    return statement, stopped, False

            case AST.NoOp():
                return statement, False, True

            case AST.Declare(variable, type):
                if variable in self.symbol_table:
                    original_declaration = next(
                        _variable
                        for _variable in self.symbol_table
                        if _variable.identifier == variable.identifier
                    )
                    raise AnalysisError(
                        f"Found declaration of variable {variable.identifier!r}...",
                        variable.location,
                        "",
                        "...that was already declared at.",
                        original_declaration.location,
                    )

                self.symbol_table[variable] = type
                return statement, False, True

            case AST.Let(variable, expression):
                self.analyze_expression(expression)
                self.analyze_variable_write(variable)

                return statement, False, False

            case AST.Stop():
                return statement, True, False

            case AST.Emit(variable):
                self.analyze_variable_read(variable)

                return statement, False, False

            case AST.If(condition, truthy_branch, falsey_branch):
                self.analyze_variable_read(condition)
                truthy_branch, truthy_stopped, truthy_elidable = (
                    self.analyze_statement(truthy_branch)
                )
                falsey_branch, falsey_stopped, falsey_elidable = (
                    self.analyze_statement(falsey_branch)
                )

                if truthy_elidable and falsey_elidable:
                    return AST.NoOp(location=statement.location), False, True
                else:
                    return (
                        AST.If(
                            condition=condition,
                            truthy_branch=truthy_branch,
                            falsey_branch=falsey_branch,
                            location=statement.location,
                        ),
                        truthy_stopped and falsey_stopped,
                        False,
                    )

            case _:
                raise AnalysisError(
                    "Found unknown statement.", statement.location
                )

    def analyze_expression(self, expression: common.Expression):
        for variable in expression.arguments:
            self.analyze_variable_read(variable)

    def analyze_variable_read(self, variable: common.Identifier):
        if variable not in self.bound_symbols:
            raise AnalysisError(
                f"Found read from uninitialised variable {variable.identifier!r}.",
                variable.location,
            )

    def analyze_variable_write(self, variable: common.Identifier):
        if variable not in self.symbol_table:
            raise AnalysisError(
                f"Found write to undeclared variable {variable.identifier!r}.",
                variable.location,
            )
        self.bound_symbols.add(variable)
