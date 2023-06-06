from functools import reduce
from typing import TypeVar

from .grammars import CFG, common


__all__ = (
    "compute_successors",
    "compute_predecessors",
    "compute_dominator_tree",
)


E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


LabelGraph = dict[CFG.BlockLabel, set[CFG.BlockLabel]]


def compute_successors(graph: CFG.Graph[E, T]) -> LabelGraph:
    def extract_labels(terminal: CFG.Terminal) -> set[CFG.BlockLabel]:
        match terminal:
          case CFG.GoTo(label, _):
              return {label}
          case CFG.Jump(label, _):
              return {label}
          case CFG.If(_, truthy, falsey):
              return extract_labels(truthy) | extract_labels(falsey)
          case _:
              return set()

    return {
        label: extract_labels(block.terminal)
        for label, block in graph.blocks.items()
    }


def compute_predecessors(graph: CFG.Graph[E, T]) -> LabelGraph:
    inverted = {
        label: set()
        for label in graph.blocks
    }
    for label, successors in compute_successors(graph).items():
        for successor in successors:
            inverted[successor].add(label)
    return inverted


def compute_dominator_tree(graph: CFG.Graph[E, T]) -> LabelGraph:
    sucessors = compute_successors(graph)
    predecessors = compute_predecessors(graph)

    dom = { graph.entry_label: {graph.entry_label} }
    for label in graph.blocks.keys() - {graph.entry_label}:
        dom[label] = set(graph.blocks.keys())

    stack = list(graph.blocks.keys() - {graph.entry_label})
    while stack:
        label = stack.pop()
        old, dom[label] = dom[label], {label} | reduce(
            lambda acc, next: dom[next].intersection(acc),
            predecessors[label],
            set(graph.blocks.keys())
        )
        if old != dom[label]:
            stack.extend(sucessors[label] - {graph.entry_label, *stack})

    return dom
