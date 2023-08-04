from functools import reduce
from typing import TypeVar, Iterator

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


def compute_loopless_successors(graph: CFG.Graph[E, T]) -> LabelGraph:
    successors = compute_successors(graph)
    for (source, sink) in get_jumps(graph):
        successors[source].remove(sink)
    return successors


def get_jumps(graph: CFG.Graph[E, T]) -> set[tuple[CFG.BlockLabel,CFG.BlockLabel]]:
    def extract_jumps(terminal: CFG.Terminal) -> set[CFG.BlockLabel]:
        match terminal:
          case CFG.GoTo(label, _):
              return set()
          case CFG.Jump(label, _):
              return {label}
          case CFG.If(_, truthy, falsey):
              return extract_jumps(truthy) | extract_jumps(falsey)
          case _:
              return set()

    return {
        (label, target)
        for label, block in graph.blocks.items()
        for target in extract_jumps(block.terminal)
    }


def compute_depth_information(graph: CFG.Graph[E, T]) -> dict[CFG.BlockLabel, int]:
    successors = compute_successors(graph)
    stack: list[tuple[int, CFG.BlockLabel, set[CFG.BlockLabel]]] = [(0, graph.entry_label, set())]
    max_depth = {}

    while stack:
        depth, label, seen = stack.pop()
        depth += 1
        max_depth[label] = depth
        if not seen:
            seen.add(label)
            stack.extend(
                (depth, child, seen)
                for child in successors[label]
            )

    return max_depth


def invert_graph(graph: LabelGraph) -> LabelGraph:
    inverted = {
        label: set()
        for label in graph
    }
    for label, successors in graph.items():
        for successor in successors:
            inverted[successor].add(label)
    return inverted


def compute_predecessors(graph: CFG.Graph[E, T]) -> LabelGraph:
    return invert_graph(compute_successors(graph))


def compute_loopless_predecessors(graph: CFG.Graph[E, T]) -> LabelGraph:
    predecessors = compute_predecessors(graph)
    for (source, sink) in get_jumps(graph):
        predecessors[sink].remove(source)
    return predecessors


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


def depth_first_order(graph: LabelGraph, start: CFG.BlockLabel) -> Iterator[CFG.BlockLabel]:
    stack = [start]
    seen = set()
    while stack:
        current = stack.pop()
        if current not in seen:
            yield current
            stack.extend(graph[current])
            seen.add(current)


def breadth_first_order(graph: LabelGraph, start: CFG.BlockLabel) -> Iterator[CFG.BlockLabel]:
    stack = [start]
    seen = set()
    while stack:
        current = stack.pop(0)
        if current not in seen:
            yield current
            stack.extend(graph[current])
            seen.add(current)


def dependent_ordering(graph: LabelGraph, start: CFG.BlockLabel) -> Iterator[CFG.BlockLabel]:
    predecessors = invert_graph(graph)
    stack = [
        label
        for label, preds in predecessors.items()
        if not preds
    ]
    seen = set()
    while stack:
        current = stack.pop(0)
        yield current
        seen.add(current)
        for child in graph[current]:
            if seen.issuperset(predecessors[child]):
                stack.append(child)
