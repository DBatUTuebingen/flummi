import itertools

from ..IR import CFG, common
from ..library import utils


def get_block_inputs[A](cfg: CFG.Graph) -> tuple[dict[CFG.Label, set[common.Identifier[A]]], set[common.Identifier[A]]]:
    loop_readers = {
        label
        for label, node in cfg.nodes.items()
        if isinstance(node, (CFG.Source, CFG.Wait))
    }

    inputs = {
        label: free_variables(node)
        for label, node in cfg.nodes.items()
    }

    loop_carried_variables = set()

    while True:
        old_inputs = inputs

        inputs = {
            label: inputs[label] | utils.union(
                inputs[successor] - bound_variables(node)
                for successor in cfg.edges[label]
            ) if not isinstance(node, (CFG.Sink, CFG.Wait)) else loop_carried_variables
            for label, node in cfg.nodes.items()
        }

        loop_carried_variables = utils.union(inputs[loop_reader] for loop_reader in loop_readers)

        for loop_reader in loop_readers:
            inputs[loop_reader] = loop_carried_variables

        if old_inputs == inputs:
            break

    return inputs, loop_carried_variables


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
