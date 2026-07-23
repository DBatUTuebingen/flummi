from __future__ import annotations

from dataclasses import dataclass, field
from enum import Flag, auto, unique
from textwrap import dedent, indent
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


def _cte(name: str, body: str) -> str:
    return f"{sql.name(name)} AS (\n{indent(dedent(body), '  ')}\n)"


@dataclass(frozen=True, slots=True)
class _QuerySlot:
    name: str

    def reference(self, qualifier: str | None = None) -> str:
        column = sql.name(self.name)
        return f"{qualifier}.{column}" if qualifier else column


@dataclass
class _TypeBatch:
    """Build one dependency-aware DuckDB query for all type operations."""

    _ctes: list[str] = field(default_factory=list)
    _current_stage: str | None = None
    _stage_index: int = 0
    _slot_index: int = 0
    result_slots: list[_QuerySlot] = field(default_factory=list)

    previous_alias = "__flummi_type_previous"

    def new_slot(self) -> _QuerySlot:
        slot = _QuerySlot(f"__flummi_type_slot_{self._slot_index}")
        self._slot_index += 1
        return slot

    def new_cte_name(self, prefix: str) -> str:
        name = f"__flummi_type_{prefix}_{self._stage_index}"
        self._stage_index += 1
        return name

    @property
    def pending_qualifier(self) -> str | None:
        if self._current_stage is None:
            return None
        return sql.name(self.previous_alias)

    def add_stage(
        self,
        columns: list[tuple[_QuerySlot, str]],
        relation_ctes: list[str] | None = None,
    ) -> None:
        stage = self.new_cte_name("stage")
        relation_ctes = relation_ctes or []

        select_items: list[str] = []
        from_clause = ""
        if self._current_stage is not None:
            previous = sql.name(self._current_stage)
            previous_alias = sql.name(self.previous_alias)
            select_items.append(f"{previous_alias}.*")
            from_clause = f"\nFROM   {previous} AS {previous_alias}"

        select_items.extend(
            f"{expression} AS {slot.reference()}"
            for slot, expression in columns
        )
        body = "SELECT " + ",\n       ".join(select_items) + from_clause

        self._ctes.extend(relation_ctes)
        self._ctes.append(_cte(stage, body))
        self._current_stage = stage

    def query(self) -> str:
        if self._current_stage is None:
            raise AssertionError("A type query needs at least one stage")
        if not self.result_slots:
            raise AssertionError("A type query needs at least one result")

        select_list = ",\n       ".join(
            slot.reference() for slot in self.result_slots
        )
        return (
            "WITH\n  "
            + ",\n  ".join(self._ctes)
            + f"\nSELECT {select_list}\nFROM   {sql.name(self._current_stage)}"
        )


@dataclass(frozen=True, slots=True)
class _TypeValue:
    sample: _QuerySlot
    type: _QuerySlot
    expression: str


@dataclass(frozen=True, slots=True)
class _Constraint:
    kind: str
    valid: _QuerySlot | None
    actual: _QuerySlot | None
    expected: _TypeValue | None
    location: errors.Location | None
    context: str
    first_variable: Variable | None = None
    variable: Variable | None = None
    expected_count: int | None = None
    actual_count: _QuerySlot | None = None


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
    _bindings: dict[Variable, _TypeValue] = field(
        init=False,
        default_factory=dict,
    )
    _bound_symbols: set[Variable] = field(
        init=False,
        default_factory=set,
    )
    _binding_types: list[tuple[Type, _TypeValue]] = field(
        init=False,
        default_factory=list,
    )
    _pending: list[tuple[_QuerySlot, str]] = field(
        init=False,
        default_factory=list,
    )
    _pending_relation_ctes: list[str] = field(
        init=False,
        default_factory=list,
    )
    _pending_bindings: set[Variable] = field(
        init=False,
        default_factory=set,
    )
    _batch: _TypeBatch = field(
        init=False,
        default_factory=_TypeBatch,
    )
    _constraints: list[_Constraint] = field(
        init=False,
        default_factory=list,
    )
    _implicit_variables: set[Variable] = field(
        init=False,
        default_factory=set,
    )
    _emitted_types: tuple[Type, ...] | None = field(
        init=False,
        default=None,
    )
    _emitted_bindings: tuple[_TypeValue, ...] | None = field(
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
    _boolean_binding: _TypeValue | None = field(init=False, default=None)

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
            self._boolean_binding = self._declared_type_value(
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
            binding = self._declared_type_value(
                type_source,
                self._program.location,
                f"system variable {name.value!r}",
            )
            self._bindings[variable] = binding
            self._binding_types.append((type, binding))
            self._pending_bindings.add(variable)

    def run(self) -> AnalysisResult:
        if (self.infer or self.typecheck) and self.database is None:
            raise TypecheckingError(
                "Typechecking requires DuckDB; install flummi[typed]."
            )

        self.analyze_statement(self._program.body)
        self._flush_pending()

        if self._database_available:
            self._resolve_type_query()

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

                    declared = Type(type.source, location=type.location)
                    self._symbol_table[variable] = declared
                    if self._database_available:
                        binding = self._declared_type_value(
                            type.source,
                            type.location,
                            f"declared type {type.source!r}",
                        )
                        self._bindings[variable] = binding
                        self._binding_types.append((declared, binding))
                        self._pending_bindings.add(variable)

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
                actual_types = [
                    self._expression_type(
                        expression,
                        expression.location,
                        f"assignment to variable {variable.identifier!r}",
                    )
                    for variable, expression in bindings.items()
                ]
                for (variable, expression), actual in zip(
                    bindings.items(), actual_types, strict=True
                ):
                    self._write(
                        variable,
                        actual,
                        expression.location,
                        f"assignment to variable {variable.identifier!r}",
                    )

            case Emit(variables):
                for variable in variables:
                    self.analyze_variable_read(variable)
                self._check_emit(statement)

            case Conditional(condition, true_branch, false_branch):
                self._add_feature(Feature.BRANCHING)
                condition_type = self._expression_type(
                    condition, condition.location, "IF condition"
                )
                if condition_type is not None and self._constraints_enabled:
                    self._stage_bindings(
                        (self._system_variables[SystemVariable.PROBE],)
                    )
                    assert self._boolean_binding is not None
                    self._add_constraint(
                        _Constraint(
                            kind="boolean",
                            valid=self._pending_result(
                                f"typeof({condition_type.expression}) = "
                                f"typeof({self._sample_reference(self._boolean_binding)})"
                            ),
                            actual=condition_type.type,
                            expected=self._boolean_binding,
                            location=condition.location,
                            context="IF condition",
                        )
                    )
                self.analyze_statement(true_branch)
                self.analyze_statement(false_branch)

            case Loop(body):
                self._add_feature(Feature.ITERATING)
                self._loop_depth += 1
                self.analyze_statement(body)
                self._loop_depth -= 1

            case Fork(variables, expression):
                actual_types, count = self._fork_type_values(
                    variables, expression
                )
                if count is not None:
                    self._add_constraint(
                        _Constraint(
                            kind="fork_count",
                            valid=None,
                            actual=None,
                            expected=None,
                            location=expression.location,
                            context="FORK",
                            expected_count=len(variables),
                            actual_count=count,
                        )
                    )
                for variable, actual in zip(
                    variables,
                    actual_types or [None] * len(variables),
                    strict=True,
                ):
                    self._write(
                        variable,
                        actual,
                        expression.location,
                        f"FORK assignment to variable {variable.identifier!r}",
                    )

            case Gather(aggregates, keys):
                for key in keys:
                    self.analyze_variable_read(key)

                actual_types = [
                    self._expression_type(
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
                    self._write(
                        variable,
                        actual,
                        expression.location,
                        f"aggregate assignment to variable {variable.identifier!r}",
                    )

            case Sync(keys):
                for key in keys:
                    self.analyze_variable_read(key)

            case _:
                raise AnalysisError(
                    "Found unknown statement.", statement.location
                )

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

    def _write(
        self,
        variable: Variable,
        actual: _TypeValue | None,
        location: errors.Location | None,
        context: str,
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
            expected = Type("", location=variable.location)
            self._symbol_table[variable] = expected
            self._bindings[variable] = actual
            self._binding_types.append((expected, actual))
            self._implicit_variables.add(variable)
            self._pending_bindings.add(variable)
        elif actual is not None and self._constraints_enabled:
            self._stage_bindings((variable,))
            self._add_constraint(
                _Constraint(
                    kind="cast",
                    valid=self._pending_result(
                        self._cast_check(actual, self._bindings[variable])
                    ),
                    actual=actual.type,
                    expected=self._bindings[variable],
                    location=location,
                    context=context,
                )
            )

        self._bound_symbols.add(variable)

    def _check_emit(self, statement: Emit) -> None:
        emitted_types = tuple(
            self._symbol_table[variable] for variable in statement.variables
        )
        if self._emitted_types is None:
            self._emitted_types = emitted_types
            self._emitted_bindings = (
                tuple(
                    self._bindings[variable] for variable in statement.variables
                )
                if self._database_available
                else None
            )
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

        if self._database_available:
            self._stage_bindings(
                tuple(statement.variables) + tuple(self._first_emit.variables)
            )
            assert self._emitted_bindings is not None
            for index, (
                variable,
                first_variable,
                binding,
                first_binding,
            ) in enumerate(
                zip(
                    statement.variables,
                    self._first_emit.variables,
                    (
                        self._bindings[variable]
                        for variable in statement.variables
                    ),
                    self._emitted_bindings,
                    strict=True,
                )
            ):
                self._add_constraint(
                    _Constraint(
                        kind="emit",
                        valid=self._pending_result(
                            f"typeof({self._sample_reference(binding)}) = "
                            f"typeof({self._sample_reference(first_binding)})"
                        ),
                        actual=binding.type,
                        expected=first_binding,
                        location=variable.location,
                        context=f"emitted column {index + 1}",
                        first_variable=first_variable,
                        variable=variable,
                    )
                )
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
            if self._same_type(type.source, first_type.source):
                continue
            raise AnalysisError(
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

    def _expression_type(
        self,
        expression: Expression,
        location: errors.Location | None,
        context: str,
        *,
        aggregate: bool = False,
    ) -> _TypeValue | None:
        for variable in expression.arguments:
            self.analyze_variable_read(variable)

        if not self._type_query_enabled:
            return None

        self._stage_bindings(expression.arguments)
        if aggregate:
            self._flush_pending()

        source = (
            self._aggregate_expression_source(expression)
            if aggregate
            else self._expression_source(expression)
        )
        return self._expression_type_value(
            source,
            location,
            context,
        )

    def _expression_source(self, expression: Expression) -> str:
        qualifier = self._batch.pending_qualifier
        return expression.source.format(
            *(
                self._sample_reference(self._bindings[variable], qualifier)
                for variable in expression.arguments
            )
        )

    def _aggregate_expression_source(self, expression: Expression) -> str:
        if self._batch._current_stage is None:
            raise AssertionError("Aggregate expression needs a previous stage")
        qualifier = sql.name(self._batch._current_stage)
        source = expression.source.format(
            *(
                self._sample_reference(self._bindings[variable], qualifier)
                for variable in expression.arguments
            )
        )
        return f"(SELECT {source} FROM {sql.name(self._batch._current_stage)})"

    def _declared_type_value(
        self,
        source: str,
        location: errors.Location | None,
        context: str,
    ) -> _TypeValue:
        sample_expression = sql.cast(sql.NULL, source)
        sample = self._pending_column(sample_expression)
        type_slot = self._pending_result(
            f"typeof({sql.paren(sample_expression)})"
        )
        return _TypeValue(sample, type_slot, sample_expression)

    def _expression_type_value(
        self,
        source: str,
        location: errors.Location | None,
        context: str,
    ) -> _TypeValue:
        if self._is_null_expression(source):
            # Keep the query bindable so the final result can report NULL as
            # an invalid inferred variable type.
            sample_expression = sql.cast(sql.NULL, "VARCHAR")
        else:
            sample_expression = f"cast_to_type(NULL, {sql.paren(source)})"
        sample = self._pending_column(sample_expression)
        type_slot = self._pending_result(f"typeof({sql.paren(source)})")
        return _TypeValue(sample, type_slot, sample_expression)

    def _fork_type_values(
        self,
        variables: list[Variable],
        expression: Expression,
    ) -> tuple[list[_TypeValue] | None, _QuerySlot | None]:
        for variable in expression.arguments:
            self.analyze_variable_read(variable)

        if not self._type_query_enabled:
            return None, None

        self._stage_bindings(expression.arguments)
        source = self._expression_source(expression)
        fork_index = self._fork_index
        self._fork_index += 1
        relation_name = self._batch.new_cte_name(f"fork_{fork_index}")
        relation_alias = f"__flummi_fork_relation_{fork_index}"
        columns = [
            f"__flummi_fork_column_{fork_index}_{index}"
            for index in range(len(variables))
        ]
        relation_alias_sql = sql.name(relation_alias)
        column_aliases = ", ".join(sql.name(column) for column in columns)
        previous = self._batch._current_stage
        previous_alias = self._batch.pending_qualifier
        lateral = (
            f"LATERAL ({dedent(source)}) AS "
            f"{relation_alias_sql}({column_aliases})"
        )
        if previous is None:
            relation_body = f"SELECT {relation_alias_sql}.*\nFROM   {lateral}"
        else:
            relation_body = (
                f"SELECT {relation_alias_sql}.*\n"
                f"FROM   {sql.name(previous)} AS {previous_alias}\n"
                f"CROSS JOIN {lateral}"
            )
        self._pending_relation_ctes.append(_cte(relation_name, relation_body))

        relation_reference = sql.name(relation_name)
        actual_values: list[_TypeValue] = []
        for column in columns:
            actual_expression = (
                f"(SELECT {relation_alias_sql}.{sql.name(column)} "
                f"FROM {relation_reference} AS {relation_alias_sql} LIMIT 0)"
            )
            sample = self._pending_column(actual_expression)
            type_slot = self._pending_result(
                f"typeof({sql.paren(actual_expression)})"
            )
            actual_values.append(
                _TypeValue(sample, type_slot, actual_expression)
            )

        count = self._pending_result(
            f"(SELECT count(*) FROM (DESCRIBE SELECT * FROM "
            f"{relation_reference}))"
        )
        return actual_values, count

    def _sample_reference(
        self,
        value: _TypeValue,
        qualifier: str | None = None,
    ) -> str:
        if qualifier is None:
            qualifier = self._batch.pending_qualifier
        return value.sample.reference(qualifier)

    def _cast_check(self, actual: _TypeValue, expected: _TypeValue) -> str:
        actual_reference = actual.expression
        expected_reference = self._sample_reference(expected)
        return (
            f"typeof(cast_to_type({actual_reference}, "
            f"{expected_reference})) = typeof({expected_reference})"
        )

    def _pending_column(self, expression: str) -> _QuerySlot:
        slot = self._batch.new_slot()
        self._pending.append((slot, expression))
        return slot

    def _pending_result(self, expression: str) -> _QuerySlot:
        slot = self._pending_column(expression)
        self._batch.result_slots.append(slot)
        return slot

    def _add_constraint(self, constraint: _Constraint) -> None:
        self._constraints.append(constraint)

    def _stage_bindings(
        self, variables: tuple[Variable, ...] | list[Variable]
    ) -> None:
        if not self._database_available:
            return
        if any(variable in self._pending_bindings for variable in variables):
            self._flush_pending()

    def _flush_pending(self) -> None:
        if not self._database_available or not self._pending:
            return
        self._batch.add_stage(self._pending, self._pending_relation_ctes)
        self._pending = []
        self._pending_relation_ctes = []
        self._pending_bindings.clear()

    def _resolve_type_query(self) -> None:
        query = self._batch.query()
        try:
            row = self._typed_database.execute(query).fetchone()
        except Exception as error:
            cast_constraints = [
                constraint
                for constraint in self._constraints
                if constraint.kind == "cast"
            ]
            if cast_constraints and "cast" in str(error).casefold():
                constraint = cast_constraints[0]
                raise TypecheckingError(
                    f"Found {constraint.context} that DuckDB cannot cast...",
                    constraint.location,
                    f"...DuckDB reported: {error}.",
                ) from error
            if any(
                constraint.kind == "fork_count"
                for constraint in self._constraints
            ):
                raise TypecheckingError(
                    "Could not typecheck FORK expression...",
                    self._program.location,
                    f"...DuckDB reported: {error}",
                ) from error
            raise TypecheckingError(
                "Could not typecheck the program...",
                self._program.location,
                f"...DuckDB reported: {error}",
            ) from error

        if row is None:
            raise TypecheckingError(
                "Could not resolve program types.", self._program.location
            )

        values = dict(zip(self._batch.result_slots, row, strict=True))
        for type, binding in self._binding_types:
            source = self._slot_value(binding.type, values)
            if not isinstance(source, str):
                raise TypecheckingError(
                    "Could not determine a variable type.", type.location
                )
            type.source = source

        for constraint in self._constraints:
            if constraint.kind == "fork_count":
                actual_count = self._slot_value(constraint.actual_count, values)
                if actual_count != constraint.expected_count:
                    raise TypecheckingError(
                        f"Found FORK with {actual_count} result columns...",
                        constraint.location,
                        f"...but it writes {constraint.expected_count} variables.",
                    )
                continue

            valid = self._slot_value(constraint.valid, values)
            if valid:
                continue

            actual = self._slot_value(constraint.actual, values)
            if constraint.kind == "boolean":
                raise TypecheckingError(
                    f"Found IF condition with type {actual!r}...",
                    constraint.location,
                    "...but expected type 'BOOLEAN'.",
                )

            expected = constraint.expected
            expected_type = (
                self._slot_value(expected.type, values)
                if expected is not None
                else None
            )
            if constraint.kind == "emit":
                assert constraint.first_variable is not None
                assert constraint.variable is not None
                error_type = (
                    TypecheckingError
                    if self._type_query_enabled
                    else AnalysisError
                )
                raise error_type(
                    f"Found type mismatch in emitted column: variable "
                    f"{constraint.variable.identifier!r} has type {actual!r}...",
                    constraint.location,
                    f"...but variable {constraint.first_variable.identifier!r} "
                    f"in the first EMIT has type {expected_type!r}.",
                    self._first_emit.location if self._first_emit else None,
                )

            raise TypecheckingError(
                f"Found {constraint.context} with type {actual!r}...",
                constraint.location,
                f"...but DuckDB cannot cast it to {expected_type!r}.",
            )

        for variable, type in self._symbol_table.items():
            if variable in self._implicit_variables and self._is_null_type(
                type.source
            ):
                raise TypecheckingError(
                    f"Could not infer a type for variable {variable.identifier!r}...",
                    variable.location,
                    f"...DuckDB returned {type.source}, which is not a valid variable type.",
                )

    def _slot_value(
        self,
        slot: _QuerySlot | None,
        values: dict[_QuerySlot, Any],
    ) -> Any:
        if slot is None:
            return None
        return values[slot]

    @staticmethod
    def _is_null_expression(source: str) -> bool:
        return source.strip().strip("()").strip().upper() == "NULL"

    @staticmethod
    def _is_null_type(source: str) -> bool:
        return source.strip('"').upper() == "NULL"

    @staticmethod
    def _same_type(left: str, right: str) -> bool:
        return left == right
