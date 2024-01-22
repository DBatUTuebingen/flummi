import argparse
from enum import Enum, unique, auto
from pathlib import Path

from . import CFG, label_graph
from .parser import parse
from .analyzer import analyze
from .lowering import lower
from .optimizer import optimize, find_traces
from .data_flow import materialize_data_flow
from .codegen import codegen

from .pretty.print import pretty, STYLE
from .pretty.dot import dot


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
    JUMP_INTO_LOOPS = auto()
    JUMP_INTO_TRACES = auto()
    JUMPS_ONLY = auto()
    EXPLICIT_MATERIALIZED = auto()
    AVOID_MULTIPLE_RECURSIVE_REFERENCE = auto()
    INJECT_TRACE_GENERATION = auto()


def main():
    parser = argparse.ArgumentParser("flummi", description="CTE-focussed compilation of imperative programs to recursive SQL.")
    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default="out.sql", help="The file to write the compilation result to.")
    parser.add_argument('-v', '--verbose', default=0, action="count", help="Control the level of verbosity.")
    parser.add_argument('-g', '--graphs', default=None, type=Path, help="Directory to write graphviz files for each transformation to.")
    parser.add_argument('-i', '--intermediates', default=None, type=Path, help="Directory to write IR representation for each transformation to.")
    parser.add_argument('-f', '--flag', action='append', choices=Flag._member_map_.keys(), help="Configure compilation.")
    parser.add_argument('-d', '--dbms', choices=['duckdb','postgres','umbra'], help="Apply DBMS specific flag set.")
    arguments = parser.parse_args()

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

    if arguments.graphs and not arguments.graphs.exists():
        arguments.graphs.mkdir()

    if arguments.intermediates and not arguments.intermediates.exists():
        arguments.intermediates.mkdir()

    printer = Printer(arguments.verbose)

    def print_stats(stats):
        printer[1](f"\033[1;2m>> \033[0m{stats!r}")

    def print_graph(graph: CFG.Graph, path: str):
        if arguments.graphs:
            with open(arguments.graphs / path, "w+") as f:
                f.write(dot(graph))
            printer[1](f"\033[1;2m>> \033[0;2;4m{arguments.graphs / path}\033[0m")

    def print_intermediate(graph: CFG.Graph, path: str):
        if arguments.intermediates:
            with open(arguments.intermediates / path, "w+") as f:
                STYLE.off()
                f.write(pretty(graph))
                STYLE.on()
            printer[1](f"\033[1;2m>> \033[0;2;4m{arguments.intermediates / path}\033[0m")

    source = arguments.infile.read()

    ast = parse(source)

    ast, symbol_table, emit_type, variable_bindings = analyze(ast)

    printer[1]("\033[1;2m[0]\033[0;36m lowering to CFG\033[0m")
    cfg = lower(ast)
    print_graph(cfg, "0_lowering.gv")
    print_intermediate(cfg, "0_lowering.flir")
    printer[2](pretty(cfg))

    printer[1]("\033[1;2m[1]\033[0;36m optimizing CFG\033[0m")
    cfg, optimizer_statistics = optimize(cfg)
    print_stats(optimizer_statistics)
    print_graph(cfg, "1_optimize.gv")
    print_intermediate(cfg, "1_optimize.flir")
    printer[2](pretty(cfg))

    printer[1](f"\033[1;2m[2]\033[0;36m placing additional JUMPs\033[0m")
    if Flag.JUMPS_ONLY in flags:
        for block in cfg.blocks.values():
            for label in cfg.blocks.keys():
                block.terminal = CFG.jumpify(block.terminal, label)
    elif Flag.JUMP_INTO_TRACES in flags:
        for trace_head, *_ in find_traces(cfg):
            for block in cfg.blocks.values():
                block.terminal = CFG.jumpify(block.terminal, trace_head)
    elif Flag.JUMP_INTO_LOOPS in flags:
        successors = label_graph.collect_successors(cfg)
        loop_heads = label_graph.loop_heads(successors)
        for block in cfg.blocks.values():
            for loop_head in loop_heads:
                block.terminal = CFG.jumpify(block.terminal, loop_head)

    print_graph(cfg, "2_additional_jumps.gv")
    print_intermediate(cfg, "2_additional_jumps.flir")
    printer[2](pretty(cfg))

    printer[1]("\033[1;2m[3]\033[0;36m materializing data flow\033[0m")
    cfg = materialize_data_flow(cfg)
    print_graph(cfg, "3_materialize_data_flow.gv")
    print_intermediate(cfg, "3_materialize_data_flow.flir")
    printer[2](pretty(cfg))

    printer[1]("\033[1;2m[4]\033[0;36m generating SQL code\033[0m")
    sql = codegen(
        cfg,
        symbol_table,
        emit_type,
        variable_bindings,
        include_trace=Flag.INJECT_TRACE_GENERATION in flags,
        explicit_materialized=Flag.EXPLICIT_MATERIALIZED in flags,
        avoid_multiple_recursive_references=Flag.AVOID_MULTIPLE_RECURSIVE_REFERENCE in flags,
    )

    if arguments.output:
        printer[1](f"\033[1;2m*\033[0;36m writing output to \033[4m'{arguments.output.name}'\033[0m")
        arguments.output.write(sql + "\n")


if __name__ == "__main__":
    main()
