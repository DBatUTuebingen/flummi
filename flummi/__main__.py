import argparse
import io
import sys
import duckdb
from pathlib import Path

from flummi.interpreter.interpreter import Interpreter
from .grammars import CFG
from .parser import parse
from .lowering import lower
from .codegen import codegen
from .transformations import *

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


def main():
    parser = argparse.ArgumentParser("flummi", description="CTE-focussed compilation of imperative programs to recursive SQL.")

    subparsers = parser.add_subparsers(dest='command')

    compiler_parser = subparsers.add_parser('compile')
    compiler_parser.add_argument('infile', type=argparse.FileType('r'))
    compiler_parser.add_argument('-o', '--output', type=argparse.FileType('w'), default="out.sql", help="The file to write the compilation result to.")
    compiler_parser.add_argument('-v', '--verbose', default=0, action="count", help="Control the level of verbosity.")
    compiler_parser.add_argument('-g', '--graphs', default=None, type=Path, help="Directory to write graphviz files for each transformation to.")
    compiler_parser.add_argument('-i', '--intermediates', default=None, type=Path, help="Directory to write IR representation for each transformation to.")

    interpret_parser = subparsers.add_parser('interpret')
    interpret_parser.add_argument('infile', type=argparse.FileType('r', encoding='utf-8'))
    interpret_parser.add_argument('-s', '--setup', default=None, type=argparse.FileType('r'))

    arguments = parser.parse_args()
    source = arguments.infile.read()

    if arguments.command == 'interpret':
        if arguments.setup:
            duckdb.execute(arguments.setup.read())            
            
        print(Interpreter().interpret(parse(source)))

    if arguments.command == 'compile':
        if arguments.graphs and not arguments.graphs.exists():
            arguments.graphs.mkdir()

        if arguments.intermediates and not arguments.intermediates.exists():
            arguments.intermediates.mkdir()

        printer = Printer(arguments.verbose)

        def print_graph(graph: CFG.Graph[str, str], path: str):
            if arguments.graphs:
                with open(arguments.graphs / path, "w+") as f:
                    f.write(dot(graph))
                printer[1](f"\033[1;2m>> \033[0;2;4m{arguments.graphs / path}\033[0m")

        def print_intermediate(graph: CFG.Graph[str, str], path: str):
            if arguments.intermediates:
                with open(arguments.intermediates / path, "w+") as f:
                    STYLE.off()
                    f.write(pretty(graph))
                    STYLE.on()
                printer[1](f"\033[1;2m>> \033[0;2;4m{arguments.intermediates / path}\033[0m")

        

        program = parse(source)

        printer[1]("\033[1;2m[0]\033[0;36m lowering to CFG\033[0m")
        graph = lower(program, "bool")
        print_graph(graph, "0_lowering.gv")
        print_intermediate(graph, "0_lowering.flir")
        printer[2](pretty(graph))

        printer[1]("\033[1;2m[1]\033[0;36m rewriting back edges\033[0m")
        graph, heads = mark_loops(graph)
        print_graph(graph, "1_mark_loops.gv")
        print_intermediate(graph, "1_mark_loops.flir")
        printer[2](pretty(graph))

        printer[1]("\033[1;2m[2]\033[0;36m minimizing linear segments\033[0m")
        graph = schedule_segments(graph, heads)
        print_graph(graph, "2_schedule_segments.gv")
        print_intermediate(graph, "2_schedule_segments.flir")
        printer[2](pretty(graph))

        printer[1]("\033[1;2m[3]\033[0;36m inlining control only blocks\033[0m")
        graph = inline_control_blocks(graph)
        print_graph(graph, "3_inline_control_blocks.gv")
        print_intermediate(graph, "3_inline_control_blocks.flir")
        printer[2](pretty(graph))

        printer[1]("\033[1;2m[4]\033[0;36m pruning unreachable blocks\033[0m")
        graph = prune_unreachable(graph)
        print_graph(graph, "4_prune_unreachable_blocks.gv")
        print_intermediate(graph, "4_prune_unreachable_blocks.flir")
        printer[2](pretty(graph))

        heads &= graph.blocks.keys()

        printer[1]("\033[1;2m[5]\033[0;36m setting block parameters\033[0m")
        graph = set_block_parameters(graph, heads)
        print_graph(graph, "5_set_block_parameters.gv")
        print_intermediate(graph, "5_set_block_parameters.flir")
        printer[2](pretty(graph))

        printer[1]("\033[1;2m[6]\033[0;36m filling dummy inputs\033[0m")
        graph = fill_dummy_inputs(graph, "NULL")
        print_graph(graph, "6_fill_dummy_inputs.gv")
        print_intermediate(graph, "6_fill_dummy_inputs.flir")
        printer[2](pretty(graph))

        printer[1]("\033[1;2m[7]\033[0;36m generating PDG annotations\033[0m")
        graph = generate_pdg_annotations(graph, heads)
        print_graph(graph, "7_generate_pdg_annotations.gv")
        print_intermediate(graph, "7_generate_pdg_annotations.flir")
        printer[2](pretty(graph))

        printer[1]("\033[1;2m[8]\033[0;36m generating SQL code\033[0m")
        result = codegen(graph)

        if arguments.output:
            printer[1](f"\033[1;2m*\033[0;36m writing output to \033[4m'{arguments.output.name}'\033[0m")
            arguments.output.write(result+ "\n")


if __name__ == "__main__":
    main()
