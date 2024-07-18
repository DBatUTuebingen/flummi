import argparse, sys
from enum import Enum, unique, auto
from pathlib import Path

# from .IR import CFG

from .compiler.parser import parse
from .compiler.analyzer import analyze
from .compiler.lowering import lower
# from .optimizer import optimize
from .compiler.data_flow import get_block_inputs
from .compiler.codegen import codegen
from .interpeter import interpret

from .library.errors import PrettyError
from .library import graph

# from .pretty import pretty, CLI_STYLE
# from .render import render

import duckdb


__all__ = (
    "cli",
)


class Printer:
    def __init__(self, verbostiy: int):
        self.verbosity = verbostiy

    def __getitem__(self, verbosity: int):
        if verbosity <= self.verbosity:
            return print
        else:
            return lambda *args, **kwargs: ...


@unique
class Flag(Enum):
    # SQL codegen tweaks
    FORCE_WITH_RECURSIVE = auto()
    EXPLICIT_MATERIALIZED = auto()
    AVOID_MULTIPLE_RECURSIVE_REFERENCES = auto()

    # additional features
    INCLUDE_TRACE_GENERATION = auto()
    INCLUDE_EMIT_ORDINALITY = auto()


def cli():
    parser = argparse.ArgumentParser("flummi", description="CTE-focussed compilation of imperative programs to recursive SQL.")
    subparsers = parser.add_subparsers(dest='command')
    parser.add_argument('infile', type=argparse.FileType('r', encoding='utf-8'))

    compiler_parser = subparsers.add_parser('compile')
    compiler_parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='utf-8'), default="out.sql", help="The file to write the compilation result to.")
    compiler_parser.add_argument('-v', '--verbose', default=0, action="count", help="Control the level of verbosity.")
    compiler_parser.add_argument('-g', '--graphs', default=None, type=Path, help="Directory to write graphviz files for each transformation to.")
    compiler_parser.add_argument('-i', '--intermediates', default=None, type=Path, help="Directory to write IR representation for each transformation to.")
    compiler_parser.add_argument('-f', '--flag', action='append', choices=Flag._member_map_.keys(), help="Configure compilation.")
    compiler_parser.add_argument('-d', '--dbms', choices=['duckdb','postgres','umbra'], help="Apply DBMS specific flag set.")

    interpreter_parser = subparsers.add_parser('interpret')
    interpreter_parser.add_argument('-s', '--setup', default=None, type=argparse.FileType('r', encoding='utf-8'), help="SQL file to execute in the DB before program interpretation.")

    analyzer_parser = subparsers.add_parser('analyze')

    arguments = parser.parse_args()

    source = arguments.infile.read()

    try:
        ast = parse(source)

        ast, symbol_tables = analyze(ast)

        match arguments.command:
            case "compile":
                ...
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

                printer = Printer(arguments.verbose)

                # if arguments.graphs and not arguments.graphs.exists():
                #     arguments.graphs.mkdir()

                # if arguments.intermediates and not arguments.intermediates.exists():
                #     arguments.intermediates.mkdir()

                # def print_stats(stats):
                #     printer[1](f"\033[1;2m>> \033[0m{stats!r}")


                # def print_graph(graph: CFG.Program, path: str):
                #     if arguments.graphs:
                #         with open(arguments.graphs / path, "w+", encoding='utf-8') as f:
                #             f.write(render(graph))
                #         printer[1](f"\033[1;2m>> \033[0;2;4m{arguments.graphs / path}\033[0m")

                # def print_intermediate(graph: CFG.Program, path: str):
                #     if arguments.intermediates:
                #         with open(arguments.intermediates / path, "w+", encoding='utf-8') as f:
                #             f.write(pretty(graph))
                #         printer[1](f"\033[1;2m>> \033[0;2;4m{arguments.intermediates / path}\033[0m")

                # printer[1]("\033[1;2m[0]\033[0;36m lowering to CFG\033[0m")
                from pprint import pprint
                cfg = lower(ast)

                sql = codegen(cfg, symbol_tables)
                print(sql)

                # print_graph(cfg, "0_lowering.gv")
                # print_intermediate(cfg, "0_lowering.flir")
                # printer[2](pretty(cfg, style=CLI_STYLE))

                # printer[1]("\033[1;2m[1]\033[0;36m optimizing CFG\033[0m")
                # cfg, optimizer_statistics = optimize(cfg)
                # print_stats(optimizer_statistics)
                # print_graph(cfg, "1_optimize.gv")
                # print_intermediate(cfg, "1_optimize.flir")
                # printer[2](pretty(cfg, style=CLI_STYLE))

                # printer[1]("\033[1;2m[3]\033[0;36m materializing data flow\033[0m")
                # cfg, data_flow_statistics = materialize_data_flow(cfg)
                # print_stats(data_flow_statistics)
                # print_graph(cfg, "3_materialize_data_flow.gv")
                # print_intermediate(cfg, "3_materialize_data_flow.flir")
                # printer[2](pretty(cfg, style=CLI_STYLE))

                # printer[1]("\033[1;2m[4]\033[0;36m generating SQL code\033[0m")
                # sql = codegen(
                #     cfg,
                #     symbol_table,
                #     ast.function.returns,
                #     include_trace=Flag.INCLUDE_TRACE_GENERATION in flags,
                #     explicit_materialized=Flag.EXPLICIT_MATERIALIZED in flags,
                #     avoid_multiple_recursive_references=Flag.AVOID_MULTIPLE_RECURSIVE_REFERENCES in flags,
                #     include_emit_order=Flag.INCLUDE_EMIT_ORDINALITY in flags,
                #     force_with_recursive=Flag.FORCE_WITH_RECURSIVE in flags,
                # )

                # if arguments.output:
                #     printer[1](f"\033[1;2m*\033[0;36m writing output to \033[4m'{arguments.output.name}'\033[0m")
                #     arguments.output.write(sql + "\n")

            case "interpret":
                if arguments.setup is not None:
                    duckdb.sql(arguments.setup.read())

                for row in interpret(ast, symbol_table):
                    print(*row)

            case "analyze":
                print("ok")

    except PrettyError as e:
        print(e.format(source), file=sys.stderr)
        sys.exit(1)
