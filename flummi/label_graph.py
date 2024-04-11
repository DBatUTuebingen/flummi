from collections.abc import Iterator
from functools import reduce
import operator as op

from .IR import CFG


type LabelGraph[A] = dict[CFG.Label[A], set[CFG.Label[A]]]


def collect_successors[A](graph: CFG.Graph[A]) -> LabelGraph[A]:
  return {
    label: CFG.successors(block)
    for label, block in graph.blocks.items()
  }


def collect_gotos[A](graph: CFG.Graph[A]) -> LabelGraph[A]:
  return {
    label: CFG.gotos(block)
    for label, block in graph.blocks.items()
  }


def collect_jumps[A](graph: CFG.Graph[A]) -> LabelGraph[A]:
  return {
    label: CFG.jumps(block)
    for label, block in graph.blocks.items()
  }


def invert_label_graph[A](graph: LabelGraph[A]) -> LabelGraph[A]:
  new = {
    label: set()
    for label in graph
  }
  for label, children in graph.items():
    for child in children:
      new[child].add(label)
  return new


def dependent_ordering[A](graph: LabelGraph[A]) -> Iterator[CFG.Label[A]]:
  predecessors = invert_label_graph(graph)
  stack = [*sorted(
    (
      label
      for label, parents in predecessors.items()
      if not parents
    )
  )]
  sorted_graph = {
    label: sorted(children)
    for label, children in graph.items()
  }
  seen = set()
  while stack:
    label = stack.pop()
    yield label
    seen.add(label)
    for child in sorted_graph[label]:
      if seen.issuperset(predecessors[child]):
        stack.append(child)


def compute_dominator_tree[A](successors: LabelGraph[A], entry_labels: set[CFG.Label[A]]) -> LabelGraph[A]:
    predecessors = invert_label_graph(successors)

    dom = {
      label: (
        {label}
        if label in entry_labels else
        set()
      )
      for label in successors
    }

    stack = list(successors.keys() - entry_labels)
    while stack:
        label = stack.pop()
        old, dom[label] = dom[label], {label} | reduce(
            lambda acc, next: dom[next].intersection(acc),
            predecessors[label],
            set(successors.keys())
        )
        if old != dom[label]:
            stack.extend(successors[label] - {*entry_labels, *stack})

    return dom


def loop_heads[A](successors: LabelGraph[A]) -> set[CFG.Label[A]]:
    predecessors = invert_label_graph(successors)

    entry_labels = {
      label
      for label, parents in predecessors.items()
      if not parents
    }

    dom = compute_dominator_tree(successors, entry_labels)

    stack = [*entry_labels]
    seen = set()
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
