from dataclasses import dataclass, field

from ..IR import AST, common

from ..library import errors

__all__ = ("analyze",)


@dataclass(frozen=True)
class AnalysisResult:
    statement: AST.Statement
    stopped: bool
    elidable: bool


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
        result = self.analyze_statement(program.body)

        if not result.stopped:
            raise AnalysisError(
                "Not all linear control paths in the top level statement are termianted by a STOP statement.",
                result.statement.location,
            )

        program.body = result.statement

        return program

    def analyze_statement(self, statement: AST.Statement) -> AnalysisResult:
        match statement:
            case AST.Block(statements):
                if not statements:
                    raise AnalysisError(
                        "Found empty block.", statement.location
                    )

                stopped = False

                new_statements: list[AST.Statement] = []
                for child_statement in statements:
                    child_result = self.analyze_statement(child_statement)
                    if not child_result.elidable:
                        new_statements.append(child_result.statement)
                        if child_result.stopped:
                            stopped = True
                            break

                if len(new_statements) == 0:
                    return AnalysisResult(
                        AST.NoOp(location=statement.location), False, True
                    )
                elif len(new_statements) == 1:
                    return AnalysisResult(new_statements[0], stopped, False)
                else:
                    statement.statements = new_statements
                    return AnalysisResult(statement, stopped, False)

            case AST.NoOp():
                return AnalysisResult(statement, False, True)

            case AST.Assignment(variable, expression):
                self.analyze_expression(expression)
                self.analyze_variable_write(variable)

                return AnalysisResult(statement, False, False)

            case AST.Stop():
                return AnalysisResult(statement, True, False)

            case AST.Emit(variable):
                self.analyze_variable_read(variable)

                return AnalysisResult(statement, False, False)

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
