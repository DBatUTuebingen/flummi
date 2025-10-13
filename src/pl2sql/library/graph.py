from collections.abc import Iterator
from functools import reduce
from graphlib import TopologicalSorter


type Graph[A] = dict[A, set[A]]


def merge[A, B](a: Graph[A], b: Graph[B]) -> Graph[A | B]:
    new: Graph[A | B] = {}

    for label in a.keys() | b.keys():
        new[label] = (
            a.get(label, default=set[A]()) | b.get(label, default=set[B]())  # pyright: ignore[reportCallIssue]
        )
        #! [note] We ignore the "call issue" here since PyLance is to weak to
        #!        detect implicit subtyping...

    return new


def invert[A](graph: Graph[A]) -> Graph[A]:
    new: Graph[A] = {label: set() for label in graph}
    for label, children in graph.items():
        for child in children:
            assert child in new, (
                "Expected successor sets for all nodes in graph."
            )
            new[child].add(label)
    return new


def topological_order[A](graph: Graph[A]) -> Iterator[A]:
    yield from TopologicalSorter(invert(graph)).static_order()


def compute_dominator_tree[A](
    successors: Graph[A], entry_labels: set[A]
) -> Graph[A]:
    predecessors = invert(successors)

    dom: Graph[A] = {
        label: ({label} if label in entry_labels else set())
        for label in successors
    }

    stack = list(successors.keys() - entry_labels)
    while stack:
        label = stack.pop()
        old, dom[label] = (
            dom[label],
            {label}
            | reduce(
                lambda acc, next: dom[next].intersection(acc),
                predecessors[label],
                set(successors.keys()),
            ),
        )
        if old != dom[label]:
            stack.extend(successors[label] - {*entry_labels, *stack})

    return dom


def loop_heads[A](successors: Graph[A]) -> set[A]:
    predecessors = invert(successors)

    entry_labels = {
        label for label, parents in predecessors.items() if not parents
    }

    dom = compute_dominator_tree(successors, entry_labels)

    stack = [*entry_labels]
    seen: set[A] = set()
    heads = entry_labels

    while stack:
        label = stack.pop()
        seen.add(label)
        for successor in successors[label]:
            if successor in dom[label]:
                heads.add(successor)
            elif successor not in seen:
                stack.append(successor)

    return heads
