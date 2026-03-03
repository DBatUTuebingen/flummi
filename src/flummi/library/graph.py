from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

from collections.abc import Iterator
from functools import reduce


type Graph[A] = dict[A, set[A]]


def merge[A, B](a: Graph[A], b: Graph[B]) -> Graph[A | B]:
    new: Graph[A | B] = {}

    for label in a.keys() | b.keys():
        new[label] = (
            a.get(label, set[A]()) | b.get(label, set[B]())  # ty:ignore[no-matching-overload]
        )
        #! [note] We ignore the "call issue" here since PyLance is to weak to
        #!        detect implicit subtyping...

    return new


def invert[A](graph: Graph[A]) -> Graph[A]:
    new: Graph[A] = {label: set() for label in graph}
    for label, children in graph.items():
        for child in children:
            new[child].add(label)
    return new


def topological_order[A: SupportsRichComparison](
    successors: Graph[A],
) -> Iterator[A]:
    predecessors = invert(successors)
    stack = [label for label, parents in predecessors.items() if not parents]
    seen: set[A] = set()
    while stack:
        yield from sorted(stack)
        new_stack: list[A] = []
        while stack:
            label = stack.pop()
            seen.add(label)
            for child in successors[label]:
                if seen.issuperset(predecessors[child]):
                    new_stack.append(child)
        stack = new_stack


def compute_dominator_tree[A](successors: Graph[A], entry_labels: set[A]) -> Graph[A]:
    predecessors = invert(successors)

    dom: Graph[A] = {
        label: ({label} if label in entry_labels else set()) for label in successors
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

    entry_labels = {label for label, parents in predecessors.items() if not parents}

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
