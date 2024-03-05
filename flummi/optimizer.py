from pprint import pprint
from dataclasses import dataclass
from operator import or_

from . import CFG
from .label_graph import *


type Statement = CFG.Assignment | CFG.Terminal[CFG.Emit]


@dataclass
class Statistics:
  blocks_before_scheduling: int
  blocks_after_scheduling: int
  number_of_traces: int


def union[T](sets: Iterator[set[T]]) -> set[T]:
    return reduce(or_, sets, set())


def optimize(graph: CFG.Graph) -> tuple[CFG.Graph, Statistics]:
  blocks_before_scheduling = len(graph.blocks)

  traces = find_traces(graph)
  number_of_traces = len(traces)
  for trace in traces:
    statements = extract_statements(graph, trace)
    dependence_graph = build_dependence_graph(statements)
    schedule = schedule_statements(dependence_graph)
    if schedule:
      graph = materialize_schedule(
        graph,
        statements,
        trace,
        schedule
      )

  graph = inline_control_only_blocks(graph)
  graph = elide_unreachable_blocks(graph)

  blocks_after_scheduling = len(graph.blocks)

  return graph, Statistics(
    blocks_before_scheduling,
    blocks_after_scheduling,
    number_of_traces
  )


type Trace = list[CFG.BlockLabel]


def find_traces(graph: CFG.Graph) -> list[Trace]:
  successors = collect_successors(graph)
  predecessors = invert_label_graph(successors)

  stack: list[tuple[int, CFG.BlockLabel]] = [(0, graph.entry_label)]
  traces = [[]]
  visited = set()

  while stack:
    trace_id, head = stack.pop()
    traces[trace_id].append(head)

    jumps = CFG.jumps(graph.blocks[head])

    if not successors[head]:
      continue

    child, *rest = successors[head]

    if (
      len(rest) == 0 and
      not jumps and
      len(predecessors[child]) == 1
    ):
      stack.append((trace_id, child))
    else:
      for child in (child, *rest):
        if child not in visited:
          next_id = len(traces)
          traces.append([])
          stack.append((next_id, child))

    visited.add(head)

  return traces


def extract_statements(graph: CFG.Graph, trace: Trace) -> list[Statement]:
  assignments = []
  for label in trace:
    assignments.extend(graph.blocks[label].assignments)
    assignments.extend(terminal for terminal in graph.blocks[label].terminals if isinstance(terminal.type, CFG.Emit))
  return assignments


type DependenceGraph = dict[int, set[int]]


def build_dependence_graph(statements: list[Statement]) -> DependenceGraph:
  writes = {}
  reads = {}

  for i, statement in enumerate(statements):
    match statement:
      case CFG.Assignment(variable, expression):
        writes[i] = variable
        reads[i] = expression.free_variables
      case CFG.Terminal(CFG.Emit(emitted_variable), truthy, falsey):
        reads[i] = {emitted_variable, *truthy, *falsey}

  dependence_graph = {
    i: {
      j
      for j in range(0, i)
      if writes.get(j) in reads[i]
      or writes.get(i) in reads[j]
    }
    for i, _ in enumerate(statements)
  }

  return dependence_graph


type Schedule = list[list[int]]


def schedule_statements(dependence_graph: DependenceGraph) -> Schedule:
  if not dependence_graph:
    return []

  unscheduled = set(dependence_graph)
  scheduled = set()
  current_timestep = []
  schedule = []

  while unscheduled:
    current_timestep = [
      i
      for i in unscheduled
      if dependence_graph[i].issubset(scheduled)
    ]

    scheduled.update(current_timestep)
    unscheduled -= scheduled
    schedule.append(current_timestep)

  return schedule


def materialize_schedule(graph: CFG.Graph, statements: list[Statement], trace: Trace, schedule: Schedule) -> CFG.Graph:
  x = 0
  for label, timestep in zip(trace, schedule):
    x += 1
    graph.blocks[label].assignments = []
    graph.blocks[label].terminals = [terminal for terminal in graph.blocks[label].terminals if not isinstance(terminal.type, CFG.Emit)]
    for i in timestep:
      statement = statements[i]
      match statement:
        case CFG.Assignment():
          graph.blocks[label].assignments.append(statement)
        case CFG.Terminal(CFG.Emit()):
          graph.blocks[label].terminals.append(statement)
  else:
    for label in trace[x:]:
      graph.blocks[label].assignments = []
      graph.blocks[label].terminals = [terminal for terminal in graph.blocks[label].terminals if not isinstance(terminal.type, CFG.Emit)]

  return graph


def inline_control_only_blocks(graph: CFG.Graph) -> CFG.Graph:
  writes = {
    label: CFG.bound_variables(block)
    for label, block in graph.blocks.items()
  }

  changed = True
  while changed:
    succ = collect_successors(graph)
    pred = invert_label_graph(succ)
    changed = False
    for label, inlinee_block in graph.blocks.items():
      if not inlinee_block.assignments:
        for inlineable in pred[label]:
          changed = True
          new_terminals = []
          for terminal in graph.blocks[inlineable].terminals:
            match terminal.type:
              case CFG.GoTo(_label) if _label == label:
                new_terminals.extend(
                  CFG.Terminal(
                    inlinee_terminal.type,
                    truthy=inlinee_terminal.truthy + terminal.truthy,
                    falsey=inlinee_terminal.falsey + terminal.falsey,
                  )
                  for inlinee_terminal in inlinee_block.terminals
                )
              case _:
                new_terminals.append(terminal)
          graph.blocks[inlineable].terminals = new_terminals
  return graph


def elide_unreachable_blocks(graph: CFG.Graph) -> CFG.Graph:
  successors = collect_successors(graph)

  stack = [graph.entry_label]
  visited = set()

  while stack:
    label = stack.pop()
    visited.add(label)
    stack.extend(successors[label] - visited)

  graph.blocks = {
    label: block
    for label, block in graph.blocks.items()
    if label in visited
  }

  return graph
