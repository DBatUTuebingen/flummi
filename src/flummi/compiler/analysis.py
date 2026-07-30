from __future__ import annotations

from dataclasses import dataclass, field
from enum import Flag, auto, unique
from typing import Any

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
from ..library import errors, sql
from .names import SystemVariable, result_column

__all__ = (
    "AnalysisError",
    "AnalysisResult",
    "Feature",
    "TypecheckingError",
    "analyze",
)


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
    implicit_variables: frozenset[Variable] = frozenset()


class AnalysisError(errors.PrettyError):
    base_exception = ValueError


class TypecheckingError(errors.PrettyError):
    base_exception = TypeError


def analyze(
    program: Program,
    *,
    infer: bool = True,
    typecheck: bool = False,
    database: Any | None = None,
    check_emit_types: bool = True,
) -> AnalysisResult:
    return Analyzer(
        program,
        infer=infer,
        typecheck=typecheck,
        database=database,
        check_emit_types=check_emit_types,
    ).run()


@dataclass
class Analyzer:
    _program: Program
    infer: bool = True
    typecheck: bool = False
    database: Any | None = None
    check_emit_types: bool = True

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
    _bindings: dict[Variable, Type] = field(
        init=False,
        default_factory=dict,
    )
    _bound_symbols: set[Variable] = field(
        init=False,
        default_factory=set,
    )
    _implicit_variables: set[Variable] = field(
        init=False,
        default_factory=set,
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
    _loop_depth: int = field(init=False, default=0)
    _fork_index: int = field(init=False, default=0)
    _boolean_binding: Type | None = field(init=False, default=None)

    @property
    def _database_available(self) -> bool:
        return self.database is not None

    @property
    def _type_query_enabled(self) -> bool:
        return self._database_available and (self.infer or self.typecheck)

    @property
    def _constraints_enabled(self) -> bool:
        return self._database_available and self.typecheck

    @property
    def _typed_database(self) -> Any:
        assert self.database is not None
        return self.database

    def __post_init__(self):
        self._add_system_variable(SystemVariable.CONTROL, "INTEGER")
        self._add_system_variable(SystemVariable.LABEL, "VARCHAR")
        self._add_system_variable(SystemVariable.ITERATION, "INTEGER")
        self._add_system_variable(SystemVariable.PROBE, "BOOLEAN")

        if self._constraints_enabled:
            self._boolean_binding = self._resolve_declared_type(
                "BOOLEAN", self._program.location, "boolean type"
            )

    def _add_feature(self, feature: Feature):
        self._features |= feature

    def _add_system_variable(self, name: SystemVariable, type_source: str):
        variable = Variable(name, location=self._program.location)
        type = Type(type_source, location=self._program.location)
        self._symbol_table[variable] = type
        self._system_variables[name] = variable
        if self._database_available:
            binding = self._resolve_declared_type(
                type_source,
                self._program.location,
                f"system variable {name.value!r}",
            )
            type.source = binding.source
            self._bindings[variable] = type

    def run(self) -> AnalysisResult:
        if (self.infer or self.typecheck) and self.database is None:
            raise TypecheckingError(
                "Typechecking requires a DuckDB executable."
            )

        self._analyze_statement(self._program.body)
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
                    result_column(index), location=variable.location
                )
                self._symbol_table[result_variable] = type
                self._result_variables.append(result_variable)

        return AnalysisResult(
            symbol_table=self._symbol_table,
            features=self._features,
            system_variables=self._system_variables,
            result_variables=tuple(self._result_variables),
            implicit_variables=frozenset(self._implicit_variables),
        )

    def _analyze_statement(self, statement: Statement) -> None:
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

                    declared = Type(type.source, location=type.location)
                    self._symbol_table[variable] = declared
                    if self._database_available:
                        binding = self._resolve_declared_type(
                            type.source,
                            type.location,
                            f"declared type {type.source!r}",
                        )
                        declared.source = binding.source
                        self._bindings[variable] = declared

            case Block(statements):
                if not statements:
                    raise AnalysisError(
                        "Found empty block.", statement.location
                    )

                self._add_feature(Feature.SEQUENCING)
                for child_statement in statements:
                    self._analyze_statement(child_statement)

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
                actual_types = [
                    self._analyze_expression(
                        expression,
                        expression.location,
                        f"assignment to variable {variable.identifier!r}",
                    )
                    for variable, expression in bindings.items()
                ]
                for (variable, expression), actual in zip(
                    bindings.items(), actual_types, strict=True
                ):
                    self._analyze_variable_write(
                        variable,
                        actual,
                        expression.location,
                        f"assignment to variable {variable.identifier!r}",
                        expression,
                    )

            case Emit(variables):
                for variable in variables:
                    self._analyze_variable_read(variable)
                self._check_emit(statement)

            case Conditional(condition, true_branch, false_branch):
                self._add_feature(Feature.BRANCHING)
                condition_type = self._analyze_expression(
                    condition, condition.location, "IF condition"
                )
                if condition_type is not None and self._constraints_enabled:
                    assert self._boolean_binding is not None
                    self._check_type_equality(
                        condition_type,
                        self._boolean_binding,
                        condition.location,
                        "IF condition",
                    )
                self._analyze_statement(true_branch)
                self._analyze_statement(false_branch)

            case Loop(body):
                self._add_feature(Feature.ITERATING)
                self._loop_depth += 1
                self._analyze_statement(body)
                self._loop_depth -= 1

            case Fork(variables, expression):
                actual_types, count = self._analyze_fork(variables, expression)
                if count is not None and count != len(variables):
                    raise TypecheckingError(
                        f"Found FORK with {count} result columns...",
                        expression.location,
                        f"...but it writes {len(variables)} variables.",
                    )
                for variable, actual in zip(
                    variables,
                    actual_types or [None] * len(variables),
                    strict=True,
                ):
                    self._analyze_variable_write(
                        variable,
                        actual,
                        expression.location,
                        f"FORK assignment to variable {variable.identifier!r}",
                    )

            case Gather(aggregates, keys):
                for key in keys:
                    self._analyze_variable_read(key)

                actual_types = [
                    self._analyze_expression(
                        expression,
                        expression.location,
                        f"aggregate assignment to variable {variable.identifier!r}",
                        aggregate=True,
                    )
                    for variable, expression in aggregates.items()
                ]
                for (variable, expression), actual in zip(
                    aggregates.items(), actual_types, strict=True
                ):
                    self._analyze_variable_write(
                        variable,
                        actual,
                        expression.location,
                        f"aggregate assignment to variable {variable.identifier!r}",
                        expression,
                        aggregate=True,
                    )

            case Sync(keys):
                for key in keys:
                    self._analyze_variable_read(key)

            case _:
                raise AnalysisError(
                    "Found unknown statement.", statement.location
                )

    def _analyze_variable_read(self, variable: Variable):
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

    def _analyze_variable_write(
        self,
        variable: Variable,
        actual: Type | None,
        location: errors.Location | None,
        context: str,
        expression: Expression | None = None,
        *,
        aggregate: bool = False,
    ) -> None:
        expected = self._symbol_table.get(variable)
        if expected is None:
            if not self.infer:
                raise AnalysisError(
                    f"Found write to undeclared variable {variable.identifier!r}.",
                    variable.location,
                    "Variables declared before here: "
                    + ", ".join(
                        repr(declared_variable.identifier)
                        for declared_variable in self._symbol_table
                    ),
                )
            if actual is None:
                raise TypecheckingError(
                    f"Could not infer a type for {context}...",
                    location,
                    "...DuckDB is required to infer undeclared variables.",
                )
            expected = actual
            self._symbol_table[variable] = expected
            self._bindings[variable] = actual
            self._implicit_variables.add(variable)
            if self._is_null_type(actual.source):
                raise TypecheckingError(
                    f"Could not infer a type for variable {variable.identifier!r}...",
                    variable.location,
                    f"...DuckDB returned {actual.source}, which is not a valid variable type.",
                )
        elif actual is not None and self._constraints_enabled:
            self._check_cast(
                actual,
                self._bindings[variable],
                location,
                context,
                expression,
                aggregate=aggregate,
            )

        self._bound_symbols.add(variable)

    def _check_emit(self, statement: Emit) -> None:
        emitted_types = tuple(
            self._symbol_table[variable] for variable in statement.variables
        )
        if self._emitted_types is None:
            self._emitted_types = emitted_types
            self._first_emit = statement
            return

        assert self._first_emit is not None
        if len(statement.variables) != len(self._first_emit.variables):
            raise AnalysisError(
                "Found EMIT with "
                + self._describe_emission(statement.variables)
                + "...",
                statement.location,
                "...but the first EMIT has "
                + self._describe_emission(self._first_emit.variables)
                + ".",
                self._first_emit.location,
            )

        if not (self.check_emit_types or self.infer or self.typecheck):
            return

        for index, (variable, first_variable, type, first_type) in enumerate(
            zip(
                statement.variables,
                self._first_emit.variables,
                (
                    self._symbol_table[variable]
                    for variable in statement.variables
                ),
                self._emitted_types,
                strict=True,
            )
        ):
            if self._same_type(type, first_type):
                continue
            error_type = (
                TypecheckingError if self._type_query_enabled else AnalysisError
            )
            raise error_type(
                f"Found type mismatch in emitted column {index + 1}: "
                + f"variable {variable.identifier!r} has type {type.source!r}...",
                variable.location,
                f"...but variable {first_variable.identifier!r} in emitted column "
                + f"{index + 1} of the first EMIT has type {first_type.source!r}.",
                first_variable.location,
            )

    @staticmethod
    def _describe_emission(variables: list[Variable]) -> str:
        count = len(variables)
        names = ", ".join(repr(variable.identifier) for variable in variables)
        return f"{count} variable{'s' if count != 1 else ''} ({names})"

    def _analyze_expression(
        self,
        expression: Expression,
        location: errors.Location | None,
        context: str,
        *,
        aggregate: bool = False,
    ) -> Type | None:
        for variable in expression.arguments:
            self._analyze_variable_read(variable)

        if not self._type_query_enabled:
            return None

        source, from_clause = self._build_expression_query_source(expression)
        if aggregate and not expression.arguments:
            from_clause = ' FROM (VALUES (1)) AS "__flummi_type_input"'
        type = self._execute_type_query(
            f"typeof({sql.paren(source)})",
            location,
            context,
            from_clause,
        )
        return type

    def _build_expression_query_source(
        self, expression: Expression
    ) -> tuple[str, str]:
        input_alias = sql.name("__flummi_type_input")
        if not expression.arguments:
            return expression.source, ""

        columns = []
        arguments = []
        for index, variable in enumerate(expression.arguments):
            column = f"__flummi_type_argument_{index}"
            columns.append(
                f"{self._build_type_sample(self._bindings[variable])} AS "
                f"{sql.name(column)}"
            )
            arguments.append(sql.variable(column, "__flummi_type_input"))
        source = expression.source.format(*arguments)
        from_clause = f" FROM (SELECT {', '.join(columns)}) AS {input_alias}"
        return source, from_clause

    def _resolve_declared_type(
        self,
        source: str,
        location: errors.Location | None,
        context: str,
    ) -> Type:
        sample_expression = sql.cast(sql.NULL, source)
        return self._execute_type_query(
            f"typeof({sql.paren(sample_expression)})",
            location,
            context,
        )

    def _analyze_fork(
        self,
        variables: list[Variable],
        expression: Expression,
    ) -> tuple[list[Type] | None, int | None]:
        for variable in expression.arguments:
            self._analyze_variable_read(variable)

        if not self._type_query_enabled:
            return None, None

        source, from_clause = self._build_expression_query_source(expression)
        input_alias = sql.name("__flummi_type_input")
        if not from_clause:
            from_clause = f' FROM (VALUES (1)) AS {input_alias}("marker")'
        relation_query = (
            f"SELECT {sql.name('relation')}.*{from_clause}"
            f" CROSS JOIN LATERAL ({source}) AS {sql.name('relation')}"
        )
        try:
            rows = self._typed_database.execute(
                f"DESCRIBE SELECT * FROM ({relation_query})"
            ).fetchall()
        except Exception as error:
            raise TypecheckingError(
                "Could not typecheck FORK expression...",
                expression.location,
                f"...DuckDB reported: {error}",
            ) from error

        values = [Type(row[1], location=expression.location) for row in rows]
        return values, len(rows)

    def _execute_type_query(
        self,
        expression: str,
        location: errors.Location | None,
        context: str,
        from_clause: str = "",
    ) -> Type:
        try:
            row = self._typed_database.execute(
                f"SELECT {expression}{from_clause}"
            ).fetchone()
        except Exception as error:
            raise TypecheckingError(
                f"Could not infer a type for {context}...",
                location,
                f"...DuckDB reported: {error}",
            ) from error

        if row is None:
            raise TypecheckingError(
                f"Could not infer a type for {context}.", location
            )
        type_source = row[0]
        if not isinstance(type_source, str):
            raise TypecheckingError(
                f"Could not determine a type for {context}.", location
            )
        return Type(type_source, location=location)

    def _check_cast(
        self,
        actual: Type,
        expected: Type,
        location: errors.Location | None,
        context: str,
        expression: Expression | None = None,
        *,
        aggregate: bool = False,
    ) -> None:
        if expression is None:
            actual_sample = self._build_type_sample(actual)
            from_clause = ""
        else:
            actual_source, from_clause = self._build_expression_query_source(
                expression
            )
            actual_sample = sql.paren(actual_source)
            if aggregate and not expression.arguments:
                from_clause = ' FROM (VALUES (1)) AS "__flummi_type_input"'

        expected_sample = self._build_type_sample(expected)
        query = (
            "SELECT cast_to_type("
            f"{actual_sample}, {expected_sample}) IS NULL{from_clause}"
        )
        try:
            self._typed_database.execute(query).fetchone()
        except Exception as error:
            if error.args[0].startswith("Conversion Error"):
                raise TypecheckingError(
                    f"Found {context} with type {actual.source!r}...",
                    location,
                    f"...DuckDB cannot cast it to {expected.source!r}, as given by...",
                    expected.location,
                ) from error
            else:
                raise error

    def _check_type_equality(
        self,
        actual: Type,
        expected: Type,
        location: errors.Location | None,
        context: str,
    ) -> None:
        if actual.source == expected.source:
            return
        raise TypecheckingError(
            f"Found {context} with type {actual.source!r}...",
            location,
            f"...but expected type {expected.source!r}.",
        )

    def _build_type_sample(self, type: Type) -> str:
        if self._is_null_type(type.source):
            return sql.NULL
        return sql.cast(sql.NULL, type.source)

    @staticmethod
    def _is_null_type(source: str) -> bool:
        return source.strip('"').upper() == "NULL"

    @staticmethod
    def _same_type(left: Type, right: Type) -> bool:
        return left.source == right.source
