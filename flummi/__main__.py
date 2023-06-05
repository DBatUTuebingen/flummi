import argparse
from pprint import pprint

from .parser import parse
from .lowering import lower
from .codegen import codegen
from .enrichment import enrich

from .pretty.CFG import pretty as prettyCFG

def main():
    parser = argparse.ArgumentParser("quack")
    parser.add_argument('infile', type=argparse.FileType('r'))
    arguments = parser.parse_args()

    print("[SOURCE]")
    source = arguments.infile.read()
    print(source)

    # print("\n[PARSING]")
    program = parse(source)
    # pprint(program)

    print("\n[LOWERING]")
    cfg = lower(program, "bool")
    print(prettyCFG(cfg))

    print("\n[ENRICHING]")
    pdg = enrich(cfg, "NULL")
    print(prettyCFG(pdg))

    print("\n[CODE GENERATION]")
    result = codegen(pdg)
    print(result)


if __name__ == "__main__":
    main()
