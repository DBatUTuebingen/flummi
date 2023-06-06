import argparse
from contextlib import contextmanager

from .parser import parse
from .lowering import lower
from .codegen import codegen
from .transformations import *

from .pretty.CFG import pretty as prettyCFG


def main():
    parser = argparse.ArgumentParser("flummi", description="CTE-focussed compilation of imperative programs to recursive SQL.")
    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default="out.sql", help="The file to write the compilation result to.")
    parser.add_argument('-v', '--verbose', default=0, action="count", help="Control the level of verbosity.")
    arguments = parser.parse_args()

    def verbose(n: int, text: str):
        if arguments.verbose >= n:
            print(text)

    source = arguments.infile.read()

    program = parse(source)

    verbose(1, "\033[1;2m*\033[0;36m lowering to CFG\033[0m")
    graph = lower(program, "bool")
    verbose(2, prettyCFG(graph))

    verbose(1, "\033[1;2m*\033[0;36m rewriting back edges\033[0m")
    graph, heads = rewrite_jumps(graph)
    verbose(2, prettyCFG(graph))

    verbose(1, "\033[1;2m*\033[0;36m minimizing linear segments\033[0m")
    graph = minimize_segments(graph, heads)
    verbose(2, prettyCFG(graph))

    verbose(1, "\033[1;2m*\033[0;36m inlining control only blocks\033[0m")
    graph = inline_control_blocks(graph)
    verbose(2, prettyCFG(graph))

    verbose(1, "\033[1;2m*\033[0;36m pruning unreachable blocks\033[0m")
    graph = prune_unreachable(graph)
    verbose(2, prettyCFG(graph))

    heads &= graph.blocks.keys()

    verbose(1, "\033[1;2m*\033[0;36m setting block parameters\033[0m")
    graph = set_block_parameters(graph, heads)
    verbose(2, prettyCFG(graph))

    verbose(1, "\033[1;2m*\033[0;36m generating PDG annotations\033[0m")
    graph = generate_pdg_annotations(graph, heads)
    verbose(2, prettyCFG(graph))

    verbose(1, "\033[1;2m*\033[0;36m filling dummy inputs\033[0m")
    graph = fill_dummy_inputs(graph, "NULL")
    if arguments.verbose > 1:
        print(prettyCFG(graph))

    verbose(1, "\033[1;2m*\033[0;36m generating SQL code\033[0m")
    result = codegen(graph)

    if arguments.output:
        verbose(1, f"\033[1;2m*\033[0;36m writing output to \033[4m'{arguments.output.name}'\033[0m")
        arguments.output.write(result+ "\n")


if __name__ == "__main__":
    main()
