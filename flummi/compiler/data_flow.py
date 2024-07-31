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

        case CFG.Emit(variables) | CFG.Assignment(_, common.Expression(_, variables)) | CFG.Fork(_, common.Expression(_, variables)) | CFG.Join(_, common.Expression(_, variables)) | CFG.Call(_, _, variables):
            return set(variables)

        case _:
            return set()


def bound_variables[A](node: CFG.Node[A]) -> set[common.Identifier[A]]:
    match node:
        case CFG.Assignment(variables, _) | CFG.Fork(variables, _) | CFG.Join(variables, _) | CFG.Call(variables, _, _):
            return set(variables)

        case _:
            return set()
