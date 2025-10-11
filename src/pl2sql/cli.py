import subprocess
import sys
from pathlib import Path
from typing import Annotated

from .IR.CFP import Graph
from .IR.pretty.render import render

from .compiler.parser import parse
from .compiler.analyzer import analyze
from .compiler.lowering import lower
from .compiler.data_flow import plan_data_flow
from .compiler.codegen import codegen

from .library.errors import PrettyError, Location


import typer

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
        Path,
        typer.Argument(
            dir_okay=False,
            file_okay=True,
            writable=True,
            help="The path to write the compiled query to.",
        ),
    ],
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
        ast = parse(source)

        analyzed_ast = analyze(ast)

        cfp = lower(analyzed_ast)

        if graph is not None:
            render_to_file(cfp, graph, dot)

        outputs = plan_data_flow(cfp)

        sql = codegen(cfp, outputs)
    except PrettyError as e:
        print(e.format(source), file=sys.stderr)
        sys.exit(1)

    with open(output, "w+") as f:
        _ = f.write(sql)


def render_to_file(graph: Graph[Location], path: Path, command: str = "dot"):
    _ = subprocess.run(
        args=[command, "-T", path.suffix[1:] or "png", "-o", path.absolute()],
        input=render(graph).encode(),
    )
