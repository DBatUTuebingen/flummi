from typing import TypeVar

from ..grammars import CFG, common
from ..algorithms import compute_successors, compute_predecessors


__all__ = (
    "minimize_segments",
)


E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


def minimize_segments(graph: CFG.Graph[E, T], heads: set[CFG.BlockLabel]) -> CFG.Graph[E, T]:
    stack = [*heads]
    seen = set()

    while stack:
        label = stack.pop()
        if label not in seen:
            seen.add(label)
            stack.extend(minimize_segment(graph, heads, label))

    return graph


def minimize_segment(graph: CFG.Graph[E, T], heads: set[CFG.BlockLabel], root: CFG.BlockLabel) -> set[CFG.BlockLabel]:
    successors = compute_successors(graph)
    predecessors = compute_predecessors(graph)

    segment_roots = set()
    segment = []

    stack = [root]
    while stack:
        label = stack.pop()
        if (children := successors[label]):
            if len(children) == 1 and children - heads:
                [child] = children
                if len(predecessors[child]) == 1:
                    segment.append(label)
                    stack.append(child)
                    continue

            segment_roots.update(children - heads)

    changed = True

    def bubble_statements(label: CFG.BlockLabel, parent_writes: set[common.Variable], succession: list[CFG.BlockLabel]) -> list[CFG.Statement]:
        nonlocal root, graph, changed

        block = graph.blocks[label]
        total_writes = set()
        to_push = []
        if label == root:
            for statement in block.statements:
                match statement:
                    case CFG.Assignment(variable, _):
                        total_writes.add(variable)
        else:
            for i, statement in enumerate(block.statements):
                match statement:
                    case CFG.Emit(common.Expression(_, free_variables)):
                        if parent_writes.isdisjoint(free_variables):
                            to_push.append(i)
                    case CFG.Assignment(variable, common.Expression(_, free_variables)):
                        if parent_writes.isdisjoint({variable} | set(free_variables)):
                            to_push.append(i)
                        else:
                            total_writes.add(variable)

        to_push = [
            block.statements.pop(i)
            for i in to_push[::-1]
        ]

        if succession:
            child = succession.pop(0)
            pushed = bubble_statements(child, total_writes, succession)
            block.statements.extend(pushed)

        if to_push:
            changed = True

        return to_push

    while changed:
        changed = False
        bubble_statements(root, set(), segment[1:])

    return segment_roots
