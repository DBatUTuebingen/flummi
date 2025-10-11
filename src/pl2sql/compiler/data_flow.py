from ..IR import CFP, common
from ..library import utils
from . import names


def plan_data_flow[A](cfg: CFP.Graph[A]):
    inputs = get_block_inputs(cfg)
    outputs = get_block_outputs(cfg, inputs)

    return outputs


def get_block_inputs[A](
    cfg: CFP.Graph[A],
) -> dict[CFP.Label[A], set[common.Identifier[A]]]:
    inputs = {label: uses(node) for label, node in cfg.nodes.items()}

    while True:
        old_inputs = inputs
        outputs = get_block_outputs(cfg, inputs)

        inputs = {
            label: inputs[label] | outputs[label] - binds(node)
            for label, node in cfg.nodes.items()
        }

        if old_inputs == inputs:
            break

    return inputs


def get_block_outputs[A](
    cfg: CFP.Graph[A],
    inputs: dict[CFP.Label[A], set[common.Identifier[A]]],
) -> dict[CFP.Label[A], set[common.Identifier[A]]]:
    return {
        label: utils.union(inputs[successor] for successor in cfg.edges[label])
        | binds(node)
        for label, node in cfg.nodes.items()
    }


def uses[A](node: CFP.Node[A]) -> set[common.Identifier[A]]:
    match node:
        case CFP.Let(_, common.Expression(_, variables)):
            return set(variables)

        case CFP.Emit(variable):
            return {variable}

        case _:
            return set()


def binds[A](node: CFP.Node[A]) -> set[common.Identifier[A]]:
    match node:
        case CFP.Start():
            return {NOTHING(node.annotation)}

        case CFP.Let(variable, _):
            return {variable}

        case CFP.Emit(_):
            return {RESULT(node.annotation)}

        case _:
            return set()


def RESULT[A](annotation: A) -> common.Identifier[A]:
    return common.Identifier(names.result, annotation=annotation)


def NOTHING[A](annotation: A) -> common.Identifier[A]:
    return common.Identifier(names.nothing, annotation=annotation)
