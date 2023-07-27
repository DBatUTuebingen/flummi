from collections import defaultdict
from dataclasses import replace
from typing import TypeVar

from ..grammars import CFG, common
from ..algorithms import compute_successors


__all__ = (
    "set_block_parameters",
)


E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


def set_paramters(terminal: CFG.Terminal, parameters: dict[CFG.BlockLabel, set[common.Variable]]) -> CFG.Terminal:
    match terminal:
        case CFG.If(_, truthy, falsey):
            truthy = set_paramters(truthy, parameters)
            falsey = set_paramters(falsey, parameters)
            return replace(
                terminal,
                truthy_terminal=truthy,
                falsey_terminal=falsey,
            )
        case CFG.GoTo(label, _) | CFG.Jump(label, _):
            return replace(
                terminal,
                arguments=list(parameters[label])
            )
        case _:
            return terminal


def set_block_parameters(graph: CFG.Graph[E, T], heads: set[CFG.BlockLabel]) -> CFG.Graph[E, T]:
    successors = compute_successors(graph)
    stack = [graph.entry_label]
    seen = set()
    bound_variables = defaultdict(set)
    parameters = defaultdict(set)

    while stack:
        label = stack.pop()
        if label not in seen:
            seen.add(label)
            stack.extend(successors[label])
            for statement in graph.blocks[label].statements:
                match statement:
                    case CFG.Emit(common.Expression(_, free_variables)):
                        parameters[label].update(free_variables)
                    case CFG.Assignment(variable, common.Expression(_, free_variables)):
                        bound_variables[label].add(variable)
                        parameters[label].update(free_variables)
            parameters[label].update(conditional_variables(graph.blocks[label].terminal) - bound_variables[label])

    changed = True

    def bubble_parameters(label: CFG.BlockLabel):
        nonlocal seen, changed

        n_parameters = len(parameters[label])
        successor_parameters = set()
        for successor in successors[label]:
            if successor not in seen:
                seen.add(successor)
                bubble_parameters(successor)
            successor_parameters |= parameters[successor]

        parameters[label].update(successor_parameters - bound_variables[label])
        if n_parameters < len(parameters[label]):
            changed = True

    while changed:
        changed = False
        seen.clear()

        root_parameters = set()
        for root in heads:
            root_parameters |= parameters[root]
        for root in heads:
            parameters[root] = root_parameters

        bubble_parameters(graph.entry_label)

    for block in graph.blocks.values():
        block.parameters = list(parameters[block.label])
        block.terminal = set_paramters(block.terminal, parameters)

    return graph


def conditional_variables(terminal: CFG.Terminal) -> set[common.Variable]:
    match terminal:
        case CFG.If(variable, truthy, falsey):
            truthy = conditional_variables(truthy)
            falsey = conditional_variables(falsey)
            return {variable} | truthy | falsey
        case _:
            return set()
