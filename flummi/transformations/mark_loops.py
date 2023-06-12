from dataclasses import replace
from typing import TypeVar

from ..grammars import CFG, common
from ..algorithms import compute_successors, compute_dominator_tree


__all__ = (
    "mark_loops",
)


E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


def mark_loops(graph: CFG.Graph[E, T]) -> tuple[CFG.Graph[E, T], set[CFG.BlockLabel]]:
    successors = compute_successors(graph)
    dom = compute_dominator_tree(graph)

    stack = [graph.entry_label]
    seen = set()
    heads = {graph.entry_label}

    while stack:
        label = stack.pop()
        seen.add(label)
        for successor in successors[label]:
            if successor in dom[label]:
                heads.add(successor)
            elif successor not in seen:
                stack.append(successor)

    for head in heads:
        for label in graph.blocks:
            graph.blocks[label].terminal = jumpify(graph.blocks[label].terminal, head)

    return graph, heads


def jumpify(terminal: CFG.Terminal, label: CFG.BlockLabel) -> CFG.Terminal:
    match terminal:
        case CFG.GoTo(_label, arguments) if _label == label:
            return CFG.Jump(label, arguments)
        case CFG.If(_, truthy, falsey):
            truthy = jumpify(truthy, label)
            falsey = jumpify(falsey, label)
            return replace(terminal, truthy_terminal=truthy, falsey_terminal=falsey)
        case _:
            return terminal
