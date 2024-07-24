import argparse, sys
from enum import Enum, unique, auto
from pathlib import Path
import subprocess

from .IR.common import Program
from .IR.pretty.dot import render

from .compiler.parser import parse
from .compiler.analyzer import analyze
from .compiler.lowering import lower
# from .optimizer import optimize
from .compiler.codegen import codegen
from .interpeter import interpret

from .library.errors import PrettyError


import duckdb


__all__ = (
    "cli",
)


@unique
class Flag(Enum):
    # SQL codegen tweaks
    EXPLICIT_MATERIALIZED = auto()
    AVOID_MULTIPLE_RECURSIVE_REFERENCES = auto()


def cli():
    parser = argparse.ArgumentParser("flummi", description="CTE-focussed compilation of imperative programs to recursive SQL.")
    subparsers = parser.add_subparsers(
        dest='command',
        required=True
    )

    compiler_parser = subparsers.add_parser('compile')
    compiler_parser.add_argument(
        'source',
        help="The PL\\Flummi source file.",
        type=argparse.FileType(mode="r"),
        default=sys.stdin,
        nargs='?'
    )
    compiler_parser.add_argument(
        '-o', '--output',
        help="The file to write the compilation result to.",
        type=argparse.FileType('w', encoding='utf-8'),
        default="out.sql",
        metavar="FILE",
    )
    compiler_parser.add_argument(
        '-q', '--quite',
        help="Disable printing to stdout.",
        default="store_true",
    )
    compiler_parser.add_argument(
        '-g', '--graph',
        help="Directory to write graphviz files for each transformation to.",
        type=Path,
        default=None,
        metavar="FILE",
    )
    compiler_parser.add_argument(
        '-f', '--flag',
        help="Configure compilation.",
        action='append',
        choices=Flag._member_map_.keys(),
    )
    compiler_parser.add_argument(
        '-d', '--dbms',
        help="Apply DBMS specific flag set.",
        choices=['duckdb','postgres','umbra'],
    )
    compiler_parser.add_argument(
        "-d", "--dot",
        help="GraphVis dot-command to use for rendering. (default: dot)",
        metavar="DOT",
        type=str,
        default="dot"
    )

    interpreter_parser = subparsers.add_parser('interpret')
    interpreter_parser.add_argument(
        'source',
        help="The PL\\Flummi source file.",
        type=argparse.FileType(mode="r"),
        default=sys.stdin,
        nargs='?'
    )
    interpreter_parser.add_argument(
        '-s', '--setup',
        help="SQL file to execute in the DB before program interpretation.",
        type=argparse.FileType('r', encoding='utf-8'),
        default=None,
    )


    analyzer_parser = subparsers.add_parser('analyze')
    analyzer_parser.add_argument(
        'source',
        help="The PL\\Flummi source file.",
        type=argparse.FileType(mode="r"),
        default=sys.stdin,
        nargs='?'
    )

    arguments = parser.parse_args()
    source = arguments.source.read()

    try:
        ast = parse(source)
        ast, symbol_tables = analyze(ast)

        match arguments.command:
            case "compile":
                flags = {
                    Flag[flag_name]
                    for flag_name in arguments.flag or []
                }

                match arguments.dbms:
                    case 'postgres':
                        flags.update({
                            Flag.AVOID_MULTIPLE_RECURSIVE_REFERENCES
                        })
                    case 'duckdb':
                        flags.update({
                            Flag.EXPLICIT_MATERIALIZED
                        })
                    case 'umbra':
                        flags.update({

                        })

                print("\033[1;2m[0]\033[0;36m lowering to CFG\033[0m")
                cfg = lower(ast)

                if arguments.graph:
                    render_to_file(
                        cfg,
                        arguments.graph
                    )
                    print(f"\033[1;2m>> \033[0;2;4m{arguments.graph}\033[0m")

                sql = codegen(cfg, symbol_tables)

                #! [info] apply possible optimizations here!

                print("\033[1;2m[2]\033[0;36m generating SQL code\033[0m")
                sql = codegen(
                    cfg,
                    symbol_tables,
                    explicit_materialized=Flag.EXPLICIT_MATERIALIZED in flags,
                    avoid_multiple_recursive_references=Flag.AVOID_MULTIPLE_RECURSIVE_REFERENCES in flags,
                )

                if arguments.output:
                    print(f"\033[1;2m*\033[0;36m writing output to \033[4m'{arguments.output.name}'\033[0m")
                    arguments.output.write(sql + "\n")

            case "interpret":
                if arguments.setup is not None:
                    duckdb.sql(arguments.setup.read())

                for row in interpret(ast, symbol_tables):
                    print(*row)

            case "analyze":
                print("ok")

    except PrettyError as e:
        print(e.format(source), file=sys.stderr)
        sys.exit(1)


def render_to_file(root: Program, path: Path, command: str = "dot"):
  subprocess.run(
    args=[command, "-T", path.suffix[1:] or "png", "-o", path.absolute()],
    input=render(root).encode()
  )
