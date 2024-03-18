from dataclasses import dataclass
from collections.abc import Iterator

from . import CFG, grammar
from .utils import *
from .label_graph import LabelGraph, collect_successors



@dataclass
class Statistics:
    number_of_variables: int
    number_of_loop_carried_variables: int


def materialize_data_flow(graph: CFG.Graph) -> tuple[CFG.Graph, Statistics]:
    inputs, loop_carried_variables = get_block_inputs(graph)
    outputs = compute_outputs(collect_successors(graph), inputs)

    number_of_variables = len(union(iter(inputs.values())))
    number_of_loop_carried_variables = len(loop_carried_variables)

    for label, block in graph.blocks.items():
        existing_bindings = CFG.bound_variables(block)
        missing_bindings = (
            (
                outputs[label] |
                union(map(CFG.free_variables, block.terminals))
            ) -
            existing_bindings
        )
        for binding in missing_bindings:
            block.assignments.append(
                CFG.Assignment(
                    [binding],
                    grammar.Expression(
                        grammar.Location(-1,-1),
                        "{0}",
                        [binding]
                    )
                )
            )

    return graph, Statistics(
        number_of_variables,
        number_of_loop_carried_variables
    )


def get_block_inputs(graph: CFG.Graph) -> tuple[dict[CFG.BlockLabel, set[CFG.grammar.Variable]], set[CFG.grammar.Variable]]:
    jump_targets = {graph.entry_label} | union(
        CFG.jumps(block)
        for block in graph.blocks.values()
    )

    inputs = {
        label: CFG.free_variables(block)
        for label, block in graph.blocks.items()
    }

    while True:
        old_inputs, inputs = inputs, {
            label: inputs[label] | union(
                inputs[successor] - CFG.bound_variables(block)
                for successor in CFG.successors(block)
            )
            for label, block in graph.blocks.items()
        }

        jump_set = union(inputs[jump_target] for jump_target in jump_targets)

        for jump_target in jump_targets:
            inputs[jump_target] = jump_set

        if old_inputs == inputs:
            break

    return inputs, jump_set


def compute_outputs(successors: LabelGraph, inputs: dict[CFG.BlockLabel, set[CFG.grammar.Variable]]) -> dict[CFG.BlockLabel, set[CFG.grammar.Variable]]:
  return {
      label: union(inputs[child] for child in children)
      for label, children in successors.items()
  }
