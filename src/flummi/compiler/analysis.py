from dataclasses import dataclass, field
from enum import Flag, auto, unique

from ..IR.AST import (
    Assignment,
    Block,
    Break,
    Conditional,
    Continue,
    Declaration,
    Emit,
    Fork,
    Gather,
    Loop,
    NoOp,
    Program,
    Statement,
    Stop,
    Sync,
)
from ..IR.common import Expression, Type, Variable
from ..library import errors
from .names import SystemVariable, result_column

__all__ = ("analyze",)


type SymbolTable = dict[Variable, Type]


@unique
class Feature(Flag):
    SEQUENCING = auto()
    BRANCHING = auto()
    ITERATING = auto()


@dataclass
class AnalysisResult:
    symbol_table: SymbolTable
    features: Feature
    system_variables: dict[SystemVariable, Variable]
    result_variables: tuple[Variable, ...]


class AnalysisError(errors.PrettyError):
    base_exception = ValueError


def analyze(program: Program) -> AnalysisResult:
    return Analyzer(program).run()


@dataclass
class Analyzer:
    _program: Program

    _features: Feature = field(
        init=False,
        default_factory=lambda: Feature(0),
    )
    _system_variables: dict[SystemVariable, Variable] = field(
        init=False,
        default_factory=dict,
    )

    _symbol_table: SymbolTable = field(
        init=False,
        default_factory=dict,
    )
    _emitted_types: tuple[Type, ...] | None = field(
        init=False,
        default=None,
    )
    _first_emit: Emit | None = field(init=False, default=None)
    _result_variables: list[Variable] = field(
        init=False,
        default_factory=list,
    )

    _bound_symbols: set[Variable] = field(
        init=False,
        default_factory=set,
    )

    _loop_depth: int = field(init=False, default=0)

    def __post_init__(self):
        self._add_system_variable(
            SystemVariable.CONTROL,
            "int",
        )
        self._add_system_variable(
            SystemVariable.LABEL,
            "text",
        )
        self._add_system_variable(
            SystemVariable.ITERATION,
            "int",
        )
        self._add_system_variable(
            SystemVariable.PROBE,
            "boolean",
        )

    def _add_feature(self, feature: Feature):
        self._features |= feature

    def _add_system_variable(self, name: SystemVariable, type_source: str):
        variable = Variable(
            name,
            location=self._program.location,
        )

        self._symbol_table[variable] = Type(
            type_source,
            location=self._program.location,
        )

        self._system_variables[name] = variable

    def run(self) -> AnalysisResult:
        self.analyze_statement(self._program.body)

        if self._emitted_types is not None:
            assert self._first_emit is not None

            for index, (type, variable) in enumerate(
                zip(
                    self._emitted_types,
                    self._first_emit.variables,
                    strict=True,
                )
            ):
                result_variable = Variable(
                    result_column(index),
                    location=variable.location,
                )
                self._symbol_table[result_variable] = type
                self._result_variables.append(result_variable)

        return AnalysisResult(
            symbol_table=self._symbol_table,
            features=self._features,
            system_variables=self._system_variables,
            result_variables=tuple(self._result_variables),
        )

    def analyze_statement(self, statement: Statement) -> None:
        match statement:
            case Declaration(variables, type):
                for variable in variables:
                    if variable in self._symbol_table:
                        old_variable = next(
                            old_variable
                            for old_variable in self._symbol_table
                            if variable == old_variable
                        )

                        raise AnalysisError(
                            f"Found declaration of variable {variable.identifier!r}...",
                            variable.location,
                            "...that was previously declared.",
                            old_variable.location,
                        )

                    self._symbol_table[variable] = type

            case Block(statements):
                if not statements:
                    raise AnalysisError(
                        "Found empty block.", statement.location
                    )

                self._add_feature(Feature.SEQUENCING)

                for child_statement in statements:
                    self.analyze_statement(child_statement)

            case NoOp() | Stop():
                return

            case Break() | Continue():
                if self._loop_depth == 0:
                    raise AnalysisError(
                        f"Found {statement.__class__.__name__.lower()} outside of loop...",
                        statement.location,
                    )
                return

            case Assignment(bindings):
                for expression in bindings.values():
                    self.analyze_expression(expression)

                for variable in bindings.keys():
                    self.analyze_variable_write(variable)

            case Emit(variables):
                for variable in variables:
                    self.analyze_variable_read(variable)

                emitted_types = tuple(
                    self._symbol_table[variable] for variable in variables
                )

                if self._emitted_types is None:
                    self._emitted_types = emitted_types
                    self._first_emit = statement
                    return

                assert self._first_emit is not None

                if len(variables) != len(self._first_emit.variables):
                    def describe_emission(variables: list[Variable]) -> str:
                        count = len(variables)
                        names = ", ".join(repr(variable.identifier) for variable in variables)
                        return f"{count} variable{'s' if count != 1 else ''} ({names})"

                    raise AnalysisError(
                        "Found EMIT with "
                        + describe_emission(variables)
                        + "...",
                        statement.location,
                        "...but the first EMIT has "
                        + describe_emission(self._first_emit.variables)
                        + ".",
                        self._first_emit.location,
                    )

                for index, (
                    variable,
                    type,
                    first_variable,
                    first_type,
                ) in enumerate(
                    zip(
                        variables,
                        emitted_types,
                        self._first_emit.variables,
                        self._emitted_types,
                        strict=True,
                    )
                ):
                    if type != first_type:
                        raise AnalysisError(
                            f"Found type mismatch in emitted column {index + 1}: "
                            + f"variable {variable.identifier!r} has type "
                            + f"{type.source!r}...",
                            variable.location,
                            f"...but variable {first_variable.identifier!r} in "
                            + f"emitted column {index + 1} of the first EMIT "
                            + f"has type {first_type.source!r}.",
                            first_variable.location,
                        )

            case Conditional(condition, true_branch, false_branch):
                self._add_feature(Feature.BRANCHING)

                self.analyze_expression(condition)
                self.analyze_statement(true_branch)
                self.analyze_statement(false_branch)

            case Loop(body):
                self._add_feature(Feature.ITERATING)

                self._loop_depth += 1
                self.analyze_statement(body)
                self._loop_depth -= 1

            case Fork(variables, expression):
                self.analyze_expression(expression)
                for variable in variables:
                    self.analyze_variable_write(variable)

            case Gather(aggregates, keys):
                for key in keys:
                    self.analyze_variable_read(key)

                for aggregate in aggregates.values():
                    self.analyze_expression(aggregate)

                for variable in aggregates.keys():
                    self.analyze_variable_write(variable)

            case Sync(keys):
                for key in keys:
                    self.analyze_variable_read(key)

            case _:
                raise AnalysisError(
                    "Found unknown statement.", statement.location
                )

    def analyze_expression(self, expression: Expression):
        for variable in expression.arguments:
            self.analyze_variable_read(variable)

    def analyze_variable_read(self, variable: Variable):
        if variable not in self._bound_symbols:
            raise AnalysisError(
                f"Found read from uninitialized variable {variable.identifier!r}.",
                variable.location,
                "Variables initialized before here: "
                + ", ".join(
                    repr(initialized_variable.identifier)
                    for initialized_variable in self._bound_symbols
                ),
            )

    def analyze_variable_write(self, variable: Variable):
        if variable not in self._symbol_table:
            raise AnalysisError(
                f"Found write to undeclared variable {variable.identifier!r}.",
                variable.location,
                "Variables declared before here: "
                + ", ".join(
                    repr(declared_variable.identifier)
                    for declared_variable in self._symbol_table
                ),
            )

        self._bound_symbols.add(variable)
