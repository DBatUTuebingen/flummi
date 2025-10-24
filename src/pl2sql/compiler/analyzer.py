from dataclasses import dataclass, field, replace
from typing import NamedTuple, Self


from . import constants
from .features import Feature, Features, FEATURE_DEPENDECIES, MINIMAL_FEATURES
from ..IR import AST, common
from ..library import errors

__all__ = ("analyze", "SymbolTable")


type SymbolTable = dict[common.Identifier, common.Type]


class AnalysisError(errors.PrettyError): ...


class AnalysisResult(NamedTuple):
    program: AST.Program
    symbol_table: SymbolTable
    system_variables: dict[constants.Names, AST.Variable]
    features: Features


def analyze(program: AST.Program) -> AnalysisResult:
    return Analyzer(program).analyze()


@dataclass(slots=True)
class Analyzer:
    program: AST.Program
    features: Features = field(init=False, default=MINIMAL_FEATURES)
    emit_type: common.Type | None = field(init=False, default=None)
    symbol_table: SymbolTable = field(init=False, default_factory=dict)
    bound_symbols: set[common.Identifier] = field(
        init=False, default_factory=set
    )

    used_loop_names: set[common.Identifier] = field(
        init=False, default_factory=set
    )
    loop_name_stack: list[common.Identifier] = field(
        init=False, default_factory=list
    )

    def analyze(self) -> AnalysisResult:
        result, stopped, _ = self.analyze_statement(self.program.body)

        if not stopped:
            raise AnalysisError(
                "Not all linear control paths in the top level statement are termianted by a STOP statement.",
            )

        self.program.body = result

        if self.emit_type is None:
            raise AnalysisError(
                "Could not find a single EMIT and thus could not determine the type of the values this program emits.",
            )

        for feature in self.features:
            if (dependencies := FEATURE_DEPENDECIES.get(feature)) is not None:
                self.features |= dependencies

        system_variables: dict[constants.Names, AST.Variable] = {}

        emit_variable = AST.Variable(
            constants.Names.RESULT, location=self.program.location
        )
        self.symbol_table[emit_variable] = replace(
            self.emit_type, location=self.program.location
        )
        system_variables[constants.Names.RESULT] = emit_variable

        if Feature.ITERATION in self.features:
            label_variable = AST.Variable(
                constants.Names.LABEL, location=self.program.location
            )
            self.symbol_table[label_variable] = common.Type(
                "TEXT", location=self.program.location
            )
            system_variables[constants.Names.LABEL] = label_variable

        return AnalysisResult(
            self.program,
            self.symbol_table,
            system_variables,
            self.features,
        )

    class StatementResult(NamedTuple):
        statement: AST.Statement
        stopped: bool = False
        elidable: bool = False

        @classmethod
        def elide(cls, statement: AST.Statement) -> Self:
            return cls(
                AST.NoOp(location=statement.location),
                stopped=False,
                elidable=False,
            )

        @classmethod
        def stop(cls, statement: AST.Statement) -> Self:
            return cls(
                statement,
                stopped=True,
                elidable=False,
            )

    def analyze_statement(self, statement: AST.Statement) -> StatementResult:
        match statement:
            case AST.Block(statements):
                self.features.add(Feature.SEQUENCING)

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
                    return self.StatementResult.elide(statement)
                elif len(new_statements) == 1:
                    return self.StatementResult(
                        new_statements[0], stopped=stopped
                    )
                else:
                    statement.statements = new_statements
                    return self.StatementResult(statement, stopped=stopped)

            case AST.NoOp():
                return self.StatementResult.elide(statement)

            case AST.Stop():
                return self.StatementResult.stop(statement)

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
                return self.StatementResult.elide(statement)

            case AST.Let(variable, expression):
                self.analyze_expression(expression)
                self.analyze_variable_write(variable)

                return self.StatementResult(statement)

            case AST.Emit(variable):
                self.analyze_variable_read(variable)

                emit_type = self.symbol_table[variable]
                if self.emit_type is None:
                    self.emit_type = replace(
                        emit_type, location=statement.location
                    )
                elif emit_type != self.emit_type:
                    raise AnalysisError(
                        f"Found conflicting emission types ({emit_type.source} vs. {self.emit_type.source}) at...",
                        statement.location,
                        "...and...",
                        self.emit_type.location,
                    )

                return self.StatementResult(statement)

            case AST.If(condition, truthy_branch, falsey_branch):
                self.features.add(Feature.BRANCHING)

                self.analyze_variable_read(condition)
                truthy_branch, truthy_stopped, truthy_elidable = (
                    self.analyze_statement(truthy_branch)
                )
                falsey_branch, falsey_stopped, falsey_elidable = (
                    self.analyze_statement(falsey_branch)
                )

                if truthy_elidable and falsey_elidable:
                    return self.StatementResult.elide(statement)
                else:
                    return self.StatementResult(
                        AST.If(
                            condition=condition,
                            truthy_branch=truthy_branch,
                            falsey_branch=falsey_branch,
                            location=statement.location,
                        ),
                        stopped=truthy_stopped and falsey_stopped,
                    )

            case AST.Loop(name, body):
                self.features.add(Feature.ITERATION)

                if name in self.used_loop_names:
                    original_label = next(
                        original_label
                        for original_label in self.used_loop_names
                        if original_label.identifier == name.identifier
                    )
                    raise AnalysisError(
                        f"Found introduction of loop name {name.identifier!r}...",
                        name.location,
                        "",
                        "...that was already introduced at.",
                        original_label.location,
                    )

                self.used_loop_names.add(name)
                self.loop_name_stack.append(name)

                body, body_stopped, body_elidable = self.analyze_statement(body)

                _label = self.loop_name_stack.pop()
                assert _label == name

                if body_elidable:
                    return self.StatementResult.elide(statement)
                else:
                    return self.StatementResult(
                        AST.Loop(name, body, location=statement.location),
                        stopped=body_stopped,
                    )

            case AST.Continue(name):
                if name not in self.loop_name_stack:
                    raise AnalysisError(
                        f"Found continue to unintroduced loop name {name.identifier!r}.",
                        name.location,
                    )

                return self.StatementResult(statement)

            case AST.Break(name):
                if name not in self.loop_name_stack:
                    raise AnalysisError(
                        f"Found break to unintroduced loop name {name.identifier!r}.",
                        name.location,
                    )

                return self.StatementResult.stop(statement)

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
