from collections.abc import Iterator
from functools import reduce

from . import CFG


type LabelGraph = dict[CFG.BlockLabel, set[CFG.BlockLabel]]


def collect_successors(graph: CFG.Graph) -> LabelGraph:
  return {
    label: CFG.successors(block)
    for label, block in graph.blocks.items()
  }


def collect_gotos(graph: CFG.Graph) -> LabelGraph:
  return {
    label: CFG.gotos(block)
    for label, block in graph.blocks.items()
  }


def collect_jumps(graph: CFG.Graph) -> LabelGraph:
  return {
    label: CFG.jumps(block)
    for label, block in graph.blocks.items()
  }


def invert_label_graph(graph: LabelGraph) -> LabelGraph:
  new = {
    label: set()
    for label in graph
  }
  for label, children in graph.items():
    for child in children:
      new[child].add(label)
  return new


def dependent_ordering(graph: LabelGraph) -> Iterator[CFG.BlockLabel]:
  predecessors = invert_label_graph(graph)
  stack = [
    label
    for label, parents in predecessors.items()
    if not parents
  ]
  seen = set()
  while stack:
    label = stack.pop()
    yield label
    seen.add(label)
    for child in graph[label]:
      if seen.issuperset(predecessors[child]):
        stack.append(child)


def compute_dominator_tree(successors: LabelGraph, entry_labels: set[CFG.BlockLabel]) -> LabelGraph:
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


def loop_heads(successors: LabelGraph) -> set[CFG.BlockLabel]:
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

