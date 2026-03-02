from dataclasses import dataclass, field

from ..IR import AST, common

from ..library import errors

__all__ = ("analyze",)


type SymbolTable = dict[AST.Variable, AST.Type]


@dataclass(frozen=True)
class AnalysisResult:
    statement: AST.Statement
    stopped: bool
    elidable: bool


class AnalysisError(errors.PrettyError): ...


def analyze(
    program: AST.Program,
) -> tuple[AST.Program, SymbolTable]:
    analyzer = Analyzer()
    program = analyzer.analyze_program(program)
    return program, analyzer.symbol_table


@dataclass
class Analyzer:
    symbol_table: SymbolTable = field(
        init=False,
        default_factory=dict,
    )
    emitted_type: AST.Type | None = field(init=False, default=None)
    bound_symbols: set[AST.Variable] = field(
        init=False,
        default_factory=set,
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
            case AST.Declaration(variable, type):
                if variable in self.symbol_table:
                    old_variable = next(
                        old_variable
                        for old_variable in self.symbol_table
                        if variable == old_variable
                    )

                    raise AnalysisError(
                        f"Found declaration of variable {variable.identifier!r}...",
                        variable.location,
                        "...that was previously declared.",
                        old_variable.location,
                    )

                self.symbol_table[variable] = type

                return AnalysisResult(
                    AST.NoOp(location=statement.location),
                    stopped=False,
                    elidable=True,
                )

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

                this_type = self.symbol_table[variable]

                if self.emitted_type:
                    if self.emitted_type != this_type:
                        raise AnalysisError(
                            f"Found type-mismatch between emits. This emits {this_type.source!r}...",
                            statement.location,
                            f"...and this emits {self.emitted_type.source!r}.",
                            self.emitted_type.location,
                        )
                else:
                    self.emitted_type = this_type
                    #! [WARN] This may clash with other things!
                    self.emitted_type.location = statement.location

                return AnalysisResult(statement, False, False)

            case AST.Conditional(condition, true_branch, false_branch):
                self.analyze_variable_read(condition)

                true_result = self.analyze_statement(true_branch)
                false_result = self.analyze_statement(false_branch)

                statement.true_branch = true_result.statement
                statement.false_branch = false_result.statement

                return AnalysisResult(
                    statement,
                    true_result.stopped and false_result.stopped,
                    true_result.elidable and false_result.elidable,
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
