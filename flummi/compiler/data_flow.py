import itertools

from ..IR import CFG, common
from ..library import utils


def get_block_inputs[A](cfg: CFG.Graph[A]) -> dict[CFG.Label, set[common.Identifier[A]]]:
    inputs = {
        label: free_variables(node)
        for label, node in cfg.nodes.items()
    }

    while True:
        old_inputs = inputs
        outputs = get_block_outputs(cfg, inputs)

        inputs = {
            label: inputs[label] | outputs[label] - bound_variables(node)
            for label, node in cfg.nodes.items()
        }

        if old_inputs == inputs:
            break

    return inputs


def get_block_outputs[A](
    cfg: CFG.Graph[A],
    inputs: dict[CFG.Label, set[common.Identifier[A]]],
) -> dict[CFG.Label, set[common.Identifier[A]]]:
    return {
        label: utils.union(
            inputs[successor]
            for successor in itertools.chain(
                cfg.edges[label],
                (
                    label
                    for label, successor in cfg.nodes.items()
                    if isinstance(successor, CFG.Source)
                    and successor.label == node.label
                ) if isinstance(node, CFG.Sink) else ()
            )
        )
        for label, node in cfg.nodes.items()
    }


def free_variables[A](node: CFG.Node[A]) -> set[common.Identifier[A]]:
    match node:
        case CFG.Conditional(truthy, falsey):
            return set(itertools.chain(truthy, falsey))

        case CFG.Assignments(assignments):
            return set(itertools.chain.from_iterable(
                assignment.expression.arguments
                for assignment in assignments
            ))

        case CFG.Fork(_, expression) | CFG.Join(_, expression):
            return set(expression.arguments)

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

        case CFG.Fork(variables, _) | CFG.Join(variables, _):
            return set(variables)

        case _:
            return set()
