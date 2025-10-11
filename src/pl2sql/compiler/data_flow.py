from ..IR import CFP, common
from ..library import utils, errors
from . import names


def plan_data_flow(program: CFP.Program):
    inputs = get_block_inputs(program.body)
    outputs = get_block_outputs(program.body, inputs)

    return outputs


def get_block_inputs(
    cfg: CFP.Graph,
) -> dict[CFP.Label, set[common.Identifier]]:
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


def get_block_outputs(
    cfg: CFP.Graph,
    inputs: dict[CFP.Label, set[common.Identifier]],
) -> dict[CFP.Label, set[common.Identifier]]:
    return {
        label: utils.union(inputs[successor] for successor in cfg.edges[label])
        | binds(node)
        for label, node in cfg.nodes.items()
    }


def uses(node: CFP.Node) -> set[common.Identifier]:
    match node:
        case CFP.Let(_, common.Expression(_, variables)):
            return set(variables)

        case CFP.Emit(variable):
            return {variable}

        case _:
            return set()


def binds(node: CFP.Node) -> set[common.Identifier]:
    match node:
        case CFP.Start():
            return {NOTHING(node.location)}

        case CFP.Let(variable, _):
            return {variable}

        case CFP.Emit(_):
            return {RESULT(node.location)}

        case _:
            return set()


def RESULT(location: errors.Location) -> common.Identifier:
    return common.Identifier(names.result, location=location)


def NOTHING(location: errors.Location) -> common.Identifier:
    return common.Identifier(names.nothing, location=location)
