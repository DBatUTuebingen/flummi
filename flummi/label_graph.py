from collections.abc import Iterator

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
