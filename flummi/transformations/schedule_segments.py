from collections import defaultdict
from typing import TypeVar

from ..grammars import CFG, common
from ..algorithms import compute_successors, compute_predecessors


__all__ = (
    "schedule_segments",
)


E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


def schedule_segments(graph: CFG.Graph[E, T], heads: set[CFG.BlockLabel]) -> CFG.Graph[E, T]:

    segments = find_segments(graph, heads)
    for root, segment in segments.items():
        schedule_segment(graph, root, segment)

    return graph


def find_segments(graph: CFG.Graph[E,T], heads: set[CFG.BlockLabel]) -> dict[CFG.BlockLabel, list[CFG.BlockLabel]]:
    successors = compute_successors(graph)
    predecessors = compute_predecessors(graph)

    segments = defaultdict(list)
    roots = {*heads}

    stack = [
        (root, root)
        for root in heads
    ]
    while stack:
        label, segment_root = stack.pop()
        segments[segment_root].append(label)
        if (children := successors[label]):
            if len(children) == 1 and children - heads:
                [child] = children
                if len(predecessors[child]) == 1:
                    stack.append((child, segment_root))
                elif child not in roots:
                    stack.append((child, child))
                    roots.add(child)
            else:
                stack.extend(
                    (new_root, new_root)
                    for new_root in children - heads
                )
                roots.update(children)

    return segments


def schedule_segment(graph: CFG.Graph[E, T], root: CFG.BlockLabel, segment: list[CFG.BlockLabel]) -> None:
    def bubble_statements(label: CFG.BlockLabel, parent_writes: set[common.Variable], succession: list[CFG.BlockLabel]) -> tuple[list[CFG.Statement], bool]:
        nonlocal root, graph

        total_writes = set()
        to_push = []
        if label == root:
            for statement in graph.blocks[label].statements:
                match statement:
                    case CFG.Assignment(variable, _):
                        total_writes.add(variable)
        else:
            for i, statement in enumerate(graph.blocks[label].statements):
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
            graph.blocks[label].statements.pop(i)
            for i in to_push[::-1]
        ]
        changed = bool(to_push)
        child_changed = False

        if succession:
            child = succession.pop(0)
            pushed, child_changed = bubble_statements(child, total_writes, succession)
            graph.blocks[label].statements.extend(pushed)

        return to_push, changed or child_changed

    changed = True
    while changed:
        _, changed = bubble_statements(root, set(), segment[1:])
