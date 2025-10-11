from dataclasses import dataclass, field

from ..IR import AST, common

from ..library import errors

__all__ = ("analyze",)


class AnalysisError(errors.PrettyError): ...


def analyze(
    program: AST.Program,
) -> AST.Program:
    return Analyzer().analyze_program(program)


@dataclass
class Analyzer:
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

                stopped = False

                new_statements: list[AST.Statement] = []
                for child_statement in statements:
                    new_child_statement, stopped, elide = (
                        self.analyze_statement(child_statement)
                    )
                    if not elide:
                        new_statements.append(new_child_statement)
                        if stopped:
                            break

                if len(new_statements) == 0:
                    return AST.NoOp(location=statement.location), False, True
                elif len(new_statements) == 1:
                    return (new_statements[0], stopped, False)
                else:
                    statement.statements = new_statements
                    return statement, stopped, False

            case AST.NoOp():
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
        self.bound_symbols.add(variable)
