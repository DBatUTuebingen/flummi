from typing import TypeVar

from ..grammars import CFG, common


__all__ = (
    "generate_pdg_annotations",
)


E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


def generate_pdg_annotations(graph: CFG.Graph[E, T], heads: set[CFG.BlockLabel]) -> CFG.Graph[E, T]:

    def walk(label: CFG.BlockLabel, terminal: CFG.Terminal, predicate: CFG.Predicate):
        nonlocal graph

        match terminal:
            case CFG.GoTo(target, arguments):
                graph.blocks[target].predecessor_references.append(CFG.FromBlock(
                    label=label,
                    arguments=arguments,
                    predicate=predicate
                ))
            case CFG.Jump(target, arguments):
                graph.jumps.append(CFG.JumpDirective(
                    origin=label,
                    destination=target,
                    parameters=arguments,
                    predicate=predicate
                ))
            case CFG.If(conditional, truthy_branch, falsey_branch):
                walk(label, truthy_branch, CFG.And(predicate, CFG.Variable(conditional)))
                walk(label, falsey_branch, CFG.And(predicate, CFG.Not(CFG.Variable(conditional))))

    for label in heads:
        graph.blocks[label].predecessor_references.append(CFG.FromLoop(expected_label=label))

    for label, block in graph.blocks.items():
        walk(label, block.terminal, CFG.Tautology())

    return graph
