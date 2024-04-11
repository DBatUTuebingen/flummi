from .IR import CFG, common
from .utils import *
from .label_graph import LabelGraph


def get_block_inputs[A](graph: CFG.Graph[A]) -> dict[CFG.Label[A], set[common.Identifier[A]]]:
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

        if old_inputs == inputs:
            break

    return inputs


def compute_outputs[A](
    successors: LabelGraph[A],
    inputs: dict[CFG.Label[A], set[common.Identifier[A]]]
) -> dict[CFG.Label[A], set[common.Identifier[A]]]:
  return {
      label: union(inputs[child] for child in children)
      for label, children in successors.items()
  }
