import argparse, sys
from enum import Enum, unique, auto
from pprint import pprint

from .parser import parse
from .analyzer import analyze
from .lowering import lower
# from .optimizer import optimize
# from .codegen import codegen
from .interpeter import interpret
from .errors import FlummiError

from .pretty.print import pretty
from .pretty.dot import dot

import duckdb


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
    AVOID_MULTIPLE_RECURSIVE_REFERENCE = auto()

    # additional features
    INCLUDE_TRACE_GENERATION = auto()
    INCLUDE_EMIT_ORDINALITY = auto()


def main():
    parser = argparse.ArgumentParser("flummi", description="CTE-focussed compilation of imperative programs to recursive SQL.")
    subparsers = parser.add_subparsers(dest='command')

    compiler_parser = subparsers.add_parser('compile')
    compiler_parser.add_argument('infile', type=argparse.FileType('r', encoding='utf-8'))
    compiler_parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='utf-8'), default="out.sql", help="The file to write the compilation result to.")
    compiler_parser.add_argument('-v', '--verbose', default=0, action="count", help="Control the level of verbosity.")
    compiler_parser.add_argument('-f', '--flag', action='append', choices=Flag._member_map_.keys(), help="Configure compilation.")
    compiler_parser.add_argument('-d', '--dbms', choices=['duckdb','postgres','umbra'], help="Apply DBMS specific flag set.")

    interpreter_parser = subparsers.add_parser('interpret')
    interpreter_parser.add_argument('infile', type=argparse.FileType('r', encoding='utf-8'))
    interpreter_parser.add_argument('-s', '--setup', default=None, type=argparse.FileType('r', encoding='utf-8'), help="SQL file to execute in the DB before program interpretation.")

    analyzer_parser = subparsers.add_parser('analyze')
    analyzer_parser.add_argument('infile', type=argparse.FileType('r', encoding='utf-8'))

    arguments = parser.parse_args()

    source = arguments.infile.read()

    try:
        ast = parse(source)

        ast, symbol_table, emit_types = analyze(ast)

        match arguments.command:
            case "compile":
                flags = {
                    Flag[flag_name]
                    for flag_name in arguments.flag or []
                }

                match arguments.dbms:
                    case 'postgres':
                        flags.update({
                            Flag.AVOID_MULTIPLE_RECURSIVE_REFERENCE
                        })
                    case 'duckdb':
                        flags.update({
                            Flag.EXPLICIT_MATERIALIZED
                        })
                    case 'umbra':
                        flags.update({

                        })

                graph = lower(ast)
                # print(dot(graph))
                print(pretty(graph))


            case "interpret":
                if arguments.setup is not None:
                    duckdb.sql(arguments.setup.read())

                for inputs, results in interpret(ast, symbol_table):
                    pretty_inputs = f"{inputs} -> "
                    print(
                        pretty_inputs +
                        ("\n" + " " * len(pretty_inputs)).join(
                            ", ".join(map(str, result)) for result in results
                        )
                    )

            case "analyze":
                print("ok")
    except FlummiError as e:
        print(e.format(source), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
