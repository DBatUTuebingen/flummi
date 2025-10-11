from dataclasses import dataclass, field, replace

from ..IR import AST

from ..library import errors
from . import parser

__all__ = ("analyze",)


class AnalysisError(errors.PrettyError): ...


def analyze(
    program: parser.Program,
) -> parser.Program:
    return Analyzer().analyze_program(program)


@dataclass
class Analyzer:
    bound_symbols: set[parser.Identifier] = field(
        init=False, default_factory=set
    )

    def analyze_program(self, program: parser.Program) -> parser.Program:
        result, stopped, _ = self.analyze_statement(program.body)

        if not stopped:
            raise AnalysisError(
                "Not all linear control paths in the top level statement are termianted by a STOP statement.",
                result.annotation,
            )

        program.body = result

        return program

    def analyze_statement(
        self, statement: parser.Statement
    ) -> tuple[parser.Statement, bool, bool]:
        match statement:
            case AST.Block(statements):
                if not statements:
                    raise AnalysisError(
                        "Found empty block.", statement.annotation
                    )

                stopped = False

                new_statements: list[parser.Statement] = []
                for child_statement in statements:
                    new_child_statement, stopped, elide = (
                        self.analyze_statement(child_statement)
                    )
                    if not elide:
                        new_statements.append(new_child_statement)
                        if stopped:
                            break

                if len(new_statements) == 1:
                    return (new_statements[0], stopped, False)
                else:
                    return (
                        replace(statement, statements=new_statements),
                        stopped,
                        len(new_statements) == 0,
                    )

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
                    "Found unknown statement.", statement.annotation
                )

    def analyze_expression(self, expression: parser.Expression):
        for variable in expression.arguments:
            self.analyze_variable_read(variable)

    def analyze_variable_read(self, variable: parser.Identifier):
        if variable not in self.bound_symbols:
            raise AnalysisError(
                f"Found read from uninitialised variable {variable.identifier!r}.",
                variable.annotation,
            )

    def analyze_variable_write(self, variable: parser.Identifier):
        self.bound_symbols.add(variable)
