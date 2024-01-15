from . import CFG
from .label_graph import *


def optimize(graph: CFG.Graph) -> CFG.Graph:
  traces = find_traces(graph)
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

  return graph

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


def extract_statements(graph: CFG.Graph, trace: Trace) -> list[CFG.Statement]:
  statements = []
  for label in trace:
    statements.extend(graph.blocks[label].statements)
  return statements


type DependenceGraph = dict[int, set[int]]


def build_dependence_graph(statements: list[CFG.Statement]) -> DependenceGraph:
  writes = {}

  for i, statement in enumerate(statements):
    match statement:
      case CFG.Assignment(variable, _):
        writes[i] = variable

  dependence_graph = {}

  for i, statement in enumerate(statements):
    match statement:
      case CFG.Emit(expression) | CFG.Assignment(_, expression):
        dependence_graph[i] = {
          j
          for j in range(0, i)
          if writes.get(j) in expression.free_variables
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


def materialize_schedule(graph: CFG.Graph, statements: list[CFG.Statement], trace: Trace, schedule: Schedule) -> CFG.Graph:
  x = 0
  for x, (label, timestep) in enumerate(zip(trace, schedule)):
    graph.blocks[label].statements = [
      statements[i]
      for i in timestep
    ]
  else:
    for label in trace[x+1:]:
      graph.blocks[label].statements = []

  return graph


def inline_control_only_blocks(graph: CFG.Graph) -> CFG.Graph:
    changed = True
    while changed:
        succ = collect_successors(graph)
        pred = invert_label_graph(succ)
        changed = False
        for label, inlinee_block in graph.blocks.items():
            if not inlinee_block.statements:
                for inlineable in pred[label]:
                    block = graph.blocks[inlineable]
                    block.terminal, _changed = inline_terminal(block.terminal, label, inlinee_block.terminal)
                    changed |= _changed
    return graph


def inline_terminal(into: CFG.Terminal, label: CFG.BlockLabel, replacement: CFG.Terminal) -> tuple[CFG.Terminal, bool]:
    match into:
        case CFG.GoTo(_label) | CFG.Jump(_label) if _label == label:
            return replacement, True
        case CFG.If(condition, truthy, falsey):
            truthy, changed_truthy = inline_terminal(truthy, label, replacement)
            falsey, changed_falsey = inline_terminal(falsey, label, replacement)
            return CFG.If(condition, truthy, falsey), changed_truthy or changed_falsey
        case _:
            return into, False


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
