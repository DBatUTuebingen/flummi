import subprocess
import sys
from importlib import import_module
from pathlib import Path
from typing import Annotated, Any, cast

import typer

from .compiler.analysis import TypecheckingError, analyze
from .compiler.generation import generate
from .compiler.lowering import lower
from .compiler.parsing import parse
from .compiler.solving import solve
from .compiler.scheming import scheme
from .IR.CFP import Plan
from .IR.pretty.render import render
from .library.errors import PrettyError

__all__ = ("cli",)

cli = typer.Typer()


@cli.command("compile")
def compile(
    input: Annotated[
        Path,
        typer.Argument(
            dir_okay=False,
            file_okay=True,
            readable=True,
            exists=True,
            help="The file to compile.",
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Argument(
            dir_okay=False,
            file_okay=True,
            writable=True,
            help="The path to write the compiled query to.",
        ),
    ] = None,
    graph: Annotated[
        Path | None,
        typer.Option(
            dir_okay=False,
            file_okay=True,
            writable=True,
            help="File to render CFP to.",
        ),
    ] = None,
    dot: Annotated[
        str, typer.Option(help="GraphVis dot-command to use for rendering.")
    ] = "dot",
    typecheck: Annotated[
        bool | None,
        typer.Option(
            "--typecheck/--no-typecheck",
            help="Typecheck SQL expressions with DuckDB (default: automatic).",
        ),
    ] = None,
    infer: Annotated[
        bool | None,
        typer.Option(
            "--infer/--no-infer",
            help="Infer undeclared variable types with DuckDB (default: automatic).",
        ),
    ] = None,
    database: Annotated[
        Path | None,
        typer.Option(
            "-d",
            "--database",
            dir_okay=False,
            file_okay=True,
            readable=True,
            exists=True,
            help="Optional DuckDB database catalog for typechecking.",
        ),
    ] = None,
):
    with open(input, "r") as f:
        source = f.read()

    try:
        program = parse(source)

        duckdb: Any | None = None
        if not (infer is False and typecheck is False and database is None):
            try:
                duckdb = cast(Any, import_module("duckdb"))
            except ModuleNotFoundError as error:
                if infer is True or typecheck is True or database is not None:
                    raise TypecheckingError(
                        "Typechecking requires DuckDB; install flummi[typed].",
                    ) from error
                infer = False
                typecheck = False
            else:
                if infer is None:
                    infer = True
                if typecheck is None:
                    typecheck = True

        connection: Any | None = None
        owns_connection = False
        if duckdb is not None:
            assert duckdb is not None

            connection = (
                duckdb.connect()
                if database is None
                else duckdb.connect(str(database), read_only=True)
            )
            owns_connection = True

        try:
            analysis = analyze(
                program,
                infer=infer,
                typecheck=typecheck,
                database=connection,
                check_emit_types=not (infer or typecheck),
            )
        finally:
            if owns_connection:
                assert connection is not None
                connection.close()

        lowered_program = lower(program)

        if graph is not None:
            render_to_file(lowered_program.body, graph, dot)

        dataflow = solve(lowered_program, analysis)

        schema = scheme(lowered_program, analysis, dataflow)

        sql = generate(lowered_program, analysis, dataflow, schema)

    except PrettyError as e:
        e.source = source
        print(e.format(), file=sys.stderr)
        sys.exit(1)

    if output:
        with open(output, "w+") as f:
            _ = f.write(sql)
    else:
        print(sql)


def render_to_file(graph: Plan, path: Path, command: str = "dot"):
    _ = subprocess.run(
        args=[command, "-T", path.suffix[1:] or "png", "-o", path.absolute()],
        input=render(graph).encode(),
    )
