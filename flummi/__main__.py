import argparse

from .parser import parse
from .lowering import lower
from .codegen import codegen
from .enrichment import *

from .pretty.CFG import pretty as prettyCFG

def main():
    parser = argparse.ArgumentParser("flummi", description="CTE-focussed compilation of imperative programs to recursive SQL.")
    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default="out.sql", help="The file to write the compilation result to.")
    parser.add_argument('-v', '--verbose', default=0, action="count", help="Control the level of verbosity.")
    arguments = parser.parse_args()

    source = arguments.infile.read()

    program = parse(source)

    if arguments.verbose > 0:
        print("\033[1;2m*\033[0;36m lowering\033[0m")
    graph = lower(program, "bool")
    if arguments.verbose > 2:
        print(prettyCFG(graph))

    if arguments.verbose > 0:
        print("\033[1;2m*\033[0;36m rewriting back edges\033[0m")
    graph, heads = rewrite_back_edges(graph)
    if arguments.verbose > 2:
        print(prettyCFG(graph))

    if arguments.verbose > 0:
        print("\033[1;2m*\033[0;36m minimizing linear segments\033[0m")
    graph = minimize_segements(graph, heads)
    if arguments.verbose > 2:
        print(prettyCFG(graph))

    if arguments.verbose > 0:
        print("\033[1;2m*\033[0;36m inlining control only blocks\033[0m")
    graph = inline_control_only_blocks(graph)
    if arguments.verbose > 2:
        print(prettyCFG(graph))

    if arguments.verbose > 0:
        print("\033[1;2m*\033[0;36m pruning unreachable blocks\033[0m")
    graph = prune_unreachable(graph)
    if arguments.verbose > 2:
        print(prettyCFG(graph))

    heads &= graph.blocks.keys()

    if arguments.verbose > 0:
        print("\033[1;2m*\033[0;36m setting block parameters\033[0m")
    graph = set_block_parameters(graph, heads)
    if arguments.verbose > 2:
        print(prettyCFG(graph))

    if arguments.verbose > 0:
        print("\033[1;2m*\033[0;36m generating PDG annotations\033[0m")
    graph = generate_pdg_annotations(graph, heads)
    if arguments.verbose > 2:
        print(prettyCFG(graph))

    if arguments.verbose > 0:
        print("\033[1;2m*\033[0;36m filling dummy inputs\033[0m")
    graph = fill_dummy_inputs(graph, "NULL")
    if arguments.verbose > 1:
        print(prettyCFG(graph))

    if arguments.verbose > 0:
        print("\033[1;2m*\033[0;36m generating SQL code\033[0m")
    result = codegen(graph)
    if arguments.verbose > 2:
        print(prettyCFG(graph))

    if arguments.output:
        if arguments.verbose > 0:
            print(f"\033[1;2m*\033[0;36m writing output to \033[4m'{arguments.output.name}'\033[0m")
        arguments.output.write(result+ "\n")


if __name__ == "__main__":
    main()
