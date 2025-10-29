from collections import defaultdict
from dataclasses import dataclass, field, replace
from typing import NamedTuple, Self


from . import constants
from .features import Feature, FEATURE_DEPENDECIES
from ..IR import AST, common
from ..library import errors

__all__ = ("analyze", "SymbolTable")


type SymbolTable = dict[common.Identifier, common.Type]


class AnalysisError(errors.PrettyError): ...


class AnalysisResult(NamedTuple):
    program: AST.Program
    symbol_table: SymbolTable
    system_variables: dict[constants.Names, AST.Variable]
    features: dict[Feature, list[errors.Location | None]]


def analyze(program: AST.Program) -> AnalysisResult:
    return Analyzer(program).analyze()


@dataclass(slots=True)
class Analyzer:
    program: AST.Program
    features: dict[Feature, list[errors.Location | None]] = field(
        init=False, default_factory=lambda: defaultdict(list)
    )
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
        self.program.body, _, _ = self.analyze_statement(self.program.body)

        if self.emit_type is None:
            raise AnalysisError(
                "Could not find a single [bold]EMIT[/bold] and thus could not determine the type of the values this program emits.",
            )

        feature_stack = list(self.features)
        while feature_stack:
            feature = feature_stack.pop()
            if (dependencies := FEATURE_DEPENDECIES.get(feature)) is not None:
                for required_feature in dependencies:
                    if required_feature not in self.features:
                        _ = self.features[feature]
                        feature_stack.append(required_feature)

        system_variables: dict[constants.Names, AST.Variable] = {}

        # The order here is important! To make our lives easier in the
        # trampoline backend, we always introduce the label as the first system
        # variable, since that is what Umbra's `umbra.trampoline` function
        # expects.

        # if Feature.ITERATION in self.features:
        label_variable = AST.Variable(
            constants.Names.LABEL, location=self.program.location
        )
        self.symbol_table[label_variable] = common.Type(
            "TEXT", location=self.program.location
        )
        system_variables[constants.Names.LABEL] = label_variable

        emit_variable = AST.Variable(
            constants.Names.RESULT, location=self.program.location
        )
        self.symbol_table[emit_variable] = replace(
            self.emit_type, location=self.program.location
        )
        system_variables[constants.Names.RESULT] = emit_variable

        iteration_variable = AST.Variable(
            constants.Names.ITERATION, location=self.program.location
        )
        self.symbol_table[iteration_variable] = common.Type(
            "int", location=self.program.location
        )
        system_variables[constants.Names.ITERATION] = iteration_variable

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
                self.features[Feature.SEQUENCING].append(statement.location)

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
                        f"Found declaration of variable [bold]{variable.identifier}[/bold]...",
                        variable.location,
                        "...that was already declared.",
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
                        emit_type, location=variable.location
                    )
                elif emit_type != self.emit_type:
                    raise AnalysisError(
                        f"Found differing type [bold]{emit_type.source}[/bold] of an emitted value...",
                        variable.location,
                        f"...to previously emitted value of type [bold]{self.emit_type.source}[/bold].",
                        self.emit_type.location,
                    )

                return self.StatementResult(statement)

            case AST.If(condition, truthy_branch, falsey_branch):
                self.features[Feature.BRANCHING].append(statement.location)

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
                self.features[Feature.ITERATION].append(statement.location)

                if name in self.used_loop_names:
                    original_label = next(
                        original_label
                        for original_label in self.used_loop_names
                        if original_label.identifier == name.identifier
                    )
                    raise AnalysisError(
                        f"Found introduction of loop name [bold]{name.identifier}[/bold]...",
                        name.location,
                        "...that was already introduced.",
                        original_label.location,
                    )

                self.used_loop_names.add(name)
                self.loop_name_stack.append(name)

                body, _, body_elidable = self.analyze_statement(body)

                _label = self.loop_name_stack.pop()
                assert _label == name

                if body_elidable:
                    return self.StatementResult.elide(statement)
                else:
                    return self.StatementResult(
                        AST.Loop(name, body, location=statement.location),
                    )

            case AST.Continue(name):
                if name not in self.loop_name_stack:
                    raise AnalysisError(
                        f"Found continue to unintroduced loop name [bold]{name.identifier}[/bold].",
                        name.location,
                    )

                return self.StatementResult(statement)

            case AST.Break(name):
                if name not in self.loop_name_stack:
                    raise AnalysisError(
                        f"Found break to unintroduced loop name [bold]{name.identifier}[/bold].",
                        name.location,
                    )

                return self.StatementResult.stop(statement)

            case AST.Fork(variables, expression):
                self.features[Feature.CONCURRENCY].append(statement.location)

                for variable in variables:
                    self.analyze_variable_write(variable)
                self.analyze_expression(expression)

                return self.StatementResult(statement)

            case AST.Gather(aggregates, keys):
                for variable, aggregate in aggregates.items():
                    self.analyze_variable_write(variable)
                    self.analyze_expression(aggregate)

                for variable in keys:
                    self.analyze_variable_read(variable)

                return self.StatementResult(statement)

            case AST.Sync(keys):
                for variable in keys:
                    self.analyze_variable_read(variable)

                if Feature.CONCURRENCY not in self.features:
                    return self.StatementResult.elide(statement)
                else:
                    return self.StatementResult(statement)

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
                f"Found read from uninitialised variable [bold]{variable.identifier}[/bold].",
                variable.location,
            )

    def analyze_variable_write(self, variable: common.Identifier):
        if variable not in self.symbol_table:
            raise AnalysisError(
                f"Found write to undeclared variable [bold]{variable.identifier}[/bold].",
                variable.location,
            )
        self.bound_symbols.add(variable)
