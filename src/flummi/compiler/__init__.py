from __future__ import annotations

from importlib import import_module
from typing import Any, cast

from ..library.sql import SQL
from ..library.errors import PrettyError
from ..IR.AST import Program
from .analysis import AnalysisResult, TypecheckingError, analyze
from .parsing import parse
from .lowering import lower
from .solving import solve
from .scheming import scheme
from .generation import generate

__all__ = ("compile",)


def _duckdb_available() -> bool:
    try:
        import_module("duckdb")
    except ModuleNotFoundError:
        return False
    return True


def _run_analysis(
    program: Program,
    *,
    typecheck: bool,
    infer: bool,
    database: Any | None,
) -> AnalysisResult:
    connection = database
    owns_connection = False

    if connection is None and not (infer or typecheck):
        return analyze(
            program,
            infer=False,
            typecheck=False,
            database=None,
            check_emit_types=True,
        )

    if connection is None:
        try:
            duckdb = cast(Any, import_module("duckdb"))
        except ModuleNotFoundError as error:
            raise TypecheckingError(
                "Typechecking requires DuckDB; install flummi[typed]."
            ) from error

        connection = duckdb.connect()
        owns_connection = True

    try:
        return analyze(
            program,
            infer=infer,
            typecheck=typecheck,
            database=connection,
            check_emit_types=not (infer or typecheck),
        )
    finally:
        if owns_connection:
            connection.close()


def compile(
    program: str | Program,
    source: str | None = None,
    *,
    typecheck: bool | None = None,
    infer: bool | None = None,
    database: Any | None = None,
) -> SQL:
    try:
        if isinstance(program, str):
            source = program
            program = parse(program)

        duckdb_available = database is not None or (
            (infer is None or typecheck is None) and _duckdb_available()
        )
        infer = duckdb_available if infer is None else infer
        typecheck = duckdb_available if typecheck is None else typecheck

        analysis = _run_analysis(
            program,
            typecheck=typecheck,
            infer=infer,
            database=database,
        )

        lowered_program = lower(program)

        dataflow = solve(lowered_program, analysis)

        schema = scheme(lowered_program, analysis, dataflow)

        sql = generate(lowered_program, analysis, dataflow, schema)

        return sql
    except PrettyError as e:
        e.source = source
        raise e
