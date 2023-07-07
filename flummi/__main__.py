import argparse
from os import makedirs
from pathlib import Path
from sys import stderr

from .grammars import CFG
from .parser import parse
from .lowering import lower
from .codegen import codegen
from .transformations import *

from .pretty.print import pretty
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
    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default="out.sql", help="The file to write the compilation result to.")
    parser.add_argument('-v', '--verbose', default=0, action="count", help="Control the level of verbosity.")
    parser.add_argument('-g', '--graph', default=None, type=Path, help="Directory to write graphviz files for each transformation too.")
    arguments = parser.parse_args()

    if arguments.graph and not arguments.graph.exists():
        arguments.graph.mkdir()

    printer = Printer(arguments.verbose)

    def print_graph(graph: CFG.Graph[str, str], path: str):
        if arguments.graph:
            with open(arguments.graph / path, "w+") as f:
                f.write(dot(graph))
            printer[1](f"\033[{40}G\033[1;2m>> \033[0;2;4m{arguments.graph / path}\033[0m")
        else:
            printer[1]("")

    source = arguments.infile.read()

    program = parse(source)

    printer[1]("\033[1;2m[0]\033[0;36m lowering to CFG\033[0m", end="")
    graph = lower(program, "bool")
    print_graph(graph, "0_lowering.gv")
    printer[2](pretty(graph))

    printer[1]("\033[1;2m[1]\033[0;36m rewriting back edges\033[0m", end="")
    graph, heads = mark_loops(graph)
    print_graph(graph, "1_mark_loops.gv")
    printer[2](pretty(graph))

    printer[1]("\033[1;2m[2]\033[0;36m minimizing linear segments\033[0m", end="")
    graph = schedule_segments(graph, heads)
    print_graph(graph, "2_schedule_segments.gv")
    printer[2](pretty(graph))

    printer[1]("\033[1;2m[3]\033[0;36m inlining control only blocks\033[0m", end="")
    graph = inline_control_blocks(graph)
    print_graph(graph, "3_inline_control_blocks.gv")
    printer[2](pretty(graph))

    printer[1]("\033[1;2m[4]\033[0;36m pruning unreachable blocks\033[0m", end="")
    graph = prune_unreachable(graph)
    print_graph(graph, "4_prune_unreachable_blocks.gv")
    printer[2](pretty(graph))

    heads &= graph.blocks.keys()

    printer[1]("\033[1;2m[5]\033[0;36m setting block parameters\033[0m", end="")
    graph = set_block_parameters(graph, heads)
    print_graph(graph, "5_set_block_parameters.gv")
    printer[2](pretty(graph))

    printer[1]("\033[1;2m[6]\033[0;36m filling dummy inputs\033[0m", end="")
    graph = fill_dummy_inputs(graph, "NULL")
    print_graph(graph, "6_fill_dummy_inputs.gv")
    printer[2](pretty(graph))

    printer[1]("\033[1;2m[7]\033[0;36m generating PDG annotations\033[0m", end="")
    graph = generate_pdg_annotations(graph, heads)
    print_graph(graph, "7_generate_pdg_annotations.gv")
    printer[2](pretty(graph))

    printer[1]("\033[1;2m[8]\033[0;36m generating SQL code\033[0m")
    result = codegen(graph)

    if arguments.output:
        printer[1](f"\033[1;2m*\033[0;36m writing output to \033[4m'{arguments.output.name}'\033[0m")
        arguments.output.write(result+ "\n")


if __name__ == "__main__":
    main()
