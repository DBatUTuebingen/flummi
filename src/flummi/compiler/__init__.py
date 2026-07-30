from __future__ import annotations

import os

from ..library.sql import SQL
from ..library.errors import PrettyError
from ..IR.AST import Program
from .analysis import AnalysisResult, TypecheckingError, analyze
from .parsing import parse
from .lowering import lower
from .solving import solve
from .scheming import scheme
from .generation import generate
from .duckdb import Connection, PathValue, find_binary

__all__ = ("compile",)


def _run_analysis(
    program: Program,
    *,
    typecheck: bool,
    infer: bool,
    database: PathValue | None,
    duckdb_binary: str | None,
) -> AnalysisResult:
    if not (infer or typecheck):
        return analyze(
            program,
            infer=False,
            typecheck=False,
            database=None,
            check_emit_types=True,
        )

    if duckdb_binary is None:
        raise TypecheckingError(
            "Typechecking requires a DuckDB executable; "
            "install DuckDB or pass duckdb_binary."
        )

    return analyze(
        program,
        infer=infer,
        typecheck=typecheck,
        database=Connection(duckdb_binary, database),
        check_emit_types=False,
    )


def compile(
    program: str | Program,
    source: str | None = None,
    *,
    typecheck: bool | None = None,
    infer: bool | None = None,
    database: PathValue | None = None,
    duckdb_binary: PathValue | None = None,
) -> SQL:
    try:
        if isinstance(program, str):
            source = program
            program = parse(program)

        binary = find_binary(duckdb_binary)
        if (
            duckdb_binary is not None
            and binary is None
            and not (infer is False and typecheck is False)
        ):
            raise TypecheckingError(
                f"Could not find DuckDB executable {os.fspath(duckdb_binary)!r}."
            )

        duckdb_available = binary is not None
        infer = duckdb_available if infer is None else infer
        typecheck = duckdb_available if typecheck is None else typecheck

        analysis = _run_analysis(
            program,
            typecheck=typecheck,
            infer=infer,
            database=database,
            duckdb_binary=binary,
        )

        lowered_program = lower(program)

        dataflow = solve(lowered_program, analysis)

        schema = scheme(lowered_program, analysis, dataflow)

        sql = generate(lowered_program, analysis, dataflow, schema)

        return sql
    except PrettyError as e:
        e.source = source
        raise e
