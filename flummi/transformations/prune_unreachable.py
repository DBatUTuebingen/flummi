from typing import TypeVar

from ..grammars import CFG, common
from ..algorithms import compute_successors


__all__ = (
    "prune_unreachable",
)

E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


def prune_unreachable(graph: CFG.Graph[E, T]) -> CFG.Graph[E, T]:
    successors = compute_successors(graph)
    seen = set()
    stack = [graph.entry_label]

    while stack:
        label = stack.pop()
        if label not in seen:
            seen.add(label)
            stack.extend(successors[label])

    for label in graph.blocks.keys() - seen:
        del graph.blocks[label]

    return graph
