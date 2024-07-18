import itertools

from ..IR import CFG, common
from ..library import utils


def get_block_inputs[A](cfg: CFG.Graph) -> tuple[dict[CFG.Label, set[common.Identifier[A]]], set[common.Identifier[A]]]:
    jump_targets = {
        label
        for label, node in cfg.nodes.items()
        if isinstance(node, CFG.Source)
    }

    inputs = {
        label: free_variables(node)
        for label, node in cfg.nodes.items()
    }

    jump_set = set()

    while True:
        old_inputs = inputs

        inputs = {
            label: inputs[label] | utils.union(
                inputs[successor] - bound_variables(node)
                for successor in cfg.edges[label]
            ) if not isinstance(node, CFG.Sink) else jump_set
            for label, node in cfg.nodes.items()
        }

        jump_set = utils.union(inputs[jump_target] for jump_target in jump_targets)

        for jump_target in jump_targets:
            inputs[jump_target] = jump_set

        if old_inputs == inputs:
            break

    return inputs, jump_set


def free_variables[A](node: CFG.Node[A]) -> set[common.Identifier[A]]:
    match node:
        case CFG.Conditional(truthy, falsey):
            return set(itertools.chain(truthy, falsey))

        case CFG.Assignments(assignments):
            return set(itertools.chain.from_iterable(
                assignment.expression.arguments
                for assignment in assignments
            ))

        case CFG.Emits(emits):
            return set(itertools.chain.from_iterable(
                emit.variables
                for emit in emits
            ))

        case _:
            return set()


def bound_variables[A](node: CFG.Node[A]) -> set[common.Identifier[A]]:
    match node:
        case CFG.Assignments(assignments):
            return set(itertools.chain.from_iterable(
                assignment.variables
                for assignment in assignments
            ))

        case _:
            return set()
