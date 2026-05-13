import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer

from .compiler.scheming import scheme
from .compiler.analysis import analyze
from .compiler.generation import generate
from .compiler.lowering import lower
from .compiler.parsing import parse
from .compiler.solving import solve
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
):
    with open(input, "r") as f:
        source = f.read()

    try:
        program = parse(source)

        analysis = analyze(program)

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
