from collections import deque, defaultdict
from dataclasses import replace
from functools import reduce
from typing import TypeVar

from .grammars import CFG, common


__all__ = (
    "enrich",
)

E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


from .pretty.CFG import pretty as prettyCFG

def enrich(graph: CFG.Graph[E, T], dummy_input: E):
    from pprint import pformat

    from .pretty.CFG import pretty as prettyCFG

    graph, heads = rewrite_back_edges(graph)
    # print("<REWRITE_BACK_EDGES>", prettyCFG(graph), "", sep="\n")

    graph = minimize_segements(graph, heads)
    # print("<MINIMIZE_SEGEMENTS>", prettyCFG(graph), "", sep="\n")

    graph = inline_control_only_blocks(graph)
    # print("<INLINE_CONTROL_ONLY_BLOCKS>", prettyCFG(graph), "", sep="\n")

    graph = prune_unreachable(graph)
    # print("<PRUNE_UNREACHABLE>", prettyCFG(graph), "", sep="\n")

    graph = set_block_parameters(graph, heads)
    # print("<SET_BLOCK_PARAMETERS>", prettyCFG(graph), "", sep="\n")

    graph = generate_pdg_annotations(graph, heads)
    # print("<GENERATE_PDG_ANNOTATIONS>", prettyCFG(graph), "", sep="\n")

    graph = fill_dummy_inputs(graph, dummy_input)
    # print("<FILL_DUMMY_INPUTS>")

    return graph


LabelGraph = dict[CFG.BlockLabel, set[CFG.BlockLabel]]


def label_graph(graph: CFG.Graph[E, T]) -> LabelGraph:
    return {
        label: target_labels(block.terminal)
        for label, block in graph.blocks.items()
    }


def invert_graph(graph: LabelGraph) -> LabelGraph:
    inverted = {
        label: set()
        for label in graph
    }
    for label, successors in graph.items():
        for successor in successors:
            inverted[successor].add(label)
    return inverted


def target_labels(terminal: CFG.Terminal) -> set[CFG.BlockLabel]:
  match terminal:
    case CFG.GoTo(label, _):
        return {label}
    case CFG.Jump(label, _):
        return {label}
    case CFG.If(_, truthy, falsey):
        return target_labels(truthy) | target_labels(falsey)
    case _:
        return set()


def dominator_tree(graph: CFG.Graph[E, T]) -> LabelGraph:
    sucessors = label_graph(graph)
    predecessors = invert_graph(sucessors)

    dom = { graph.entry_label: {graph.entry_label} }
    for label in graph.blocks.keys() - {graph.entry_label}:
        dom[label] = set(graph.blocks.keys())

    stack = list(graph.blocks.keys() - {graph.entry_label})
    while stack:
        label = stack.pop()
        old, dom[label] = dom[label], {label} | reduce(
            lambda acc, next: dom[next].intersection(acc),
            predecessors[label],
            set(graph.blocks.keys())
        )
        if old != dom[label]:
            stack.extend(sucessors[label] - {graph.entry_label, *stack})

    return dom


def terminal_only_blocks(graph: CFG.Graph[E, T]) -> dict[CFG.BlockLabel, CFG.Terminal]:
    return {
        label: block.terminal
        for label, block in graph.blocks.items()
        if block.statements == []
    }


def inline_control_only_blocks(graph: CFG.Graph[E, T]) -> CFG.Graph[E, T]:
    changed = True
    while changed:
        dom = dominator_tree(graph)
        changed = False
        for label, inlinee in terminal_only_blocks(graph).items():
            for inlineable in dom[label] - {label}:
                block = graph.blocks[inlineable]
                block.terminal, _changed = inline_terminal(block.terminal, label, inlinee)
                changed |= _changed
    return graph


def inline_terminal(terminal: CFG.Terminal, label: CFG.BlockLabel, inlinee: CFG.Terminal) -> tuple[CFG.Terminal, bool]:
    match terminal:
        case CFG.GoTo(_label, _) | CFG.Jump(_label, _) if _label == label:
            return inlinee, True
        case CFG.If(_, truthy, falsey):
            truthy, changed_truthy = inline_terminal(truthy, label, inlinee)
            falsey, changed_falsey = inline_terminal(falsey, label, inlinee)
            return replace(terminal, truthy_terminal=truthy, falsey_terminal=falsey), changed_truthy or changed_falsey
        case _:
            return terminal, False


def prune_unreachable(graph: CFG.Graph[E, T]) -> CFG.Graph[E, T]:
    successors = label_graph(graph)
    seen = set()
    stack = [graph.entry_label]

    while stack:
        label = stack.pop()
        if label not in seen:
            seen.add(label)
            stack.extend(successors[label])

    for label in graph.blocks.keys() - seen:
        del graph.blocks[label]

    return graph


def jumpify(terminal: CFG.Terminal, label: CFG.BlockLabel) -> CFG.Terminal:
    match terminal:
        case CFG.GoTo(_label, arguments) if _label == label:
            return CFG.Jump(label, arguments)
        case CFG.If(_, truthy, falsey):
            truthy = jumpify(truthy, label)
            falsey = jumpify(falsey, label)
            return replace(terminal, truthy_terminal=truthy, falsey_terminal=falsey)
        case _:
            return terminal


def rewrite_back_edges(graph: CFG.Graph[E, T]) -> tuple[CFG.Graph[E, T], set[CFG.BlockLabel]]:
    successors = label_graph(graph)
    dom = dominator_tree(graph)

    stack = [graph.entry_label]
    seen = set()
    heads = {graph.entry_label}

    while stack:
        label = stack.pop()
        seen.add(label)
        for successor in successors[label]:
            if successor in dom[label]:
                heads.add(successor)
            elif successor not in seen:
                stack.append(successor)

    for head in heads:
        for label in graph.blocks:
            graph.blocks[label].terminal = jumpify(graph.blocks[label].terminal, head)

    return graph, heads


def minimize_segements(graph: CFG.Graph[E, T], heads: set[CFG.BlockLabel]) -> CFG.Graph[E, T]:
    stack = [*heads]
    seen = set()

    while stack:
        label = stack.pop()
        if label not in seen:
            seen.add(label)
            stack.extend(minimize_segment(graph, heads, label))

    return graph


def minimize_segment(graph: CFG.Graph[E, T], heads: set[CFG.BlockLabel], root: CFG.BlockLabel) -> set[CFG.BlockLabel]:
    successors = label_graph(graph)
    predecessors = invert_graph(successors)

    segment_roots = set()
    segment = []

    stack = [root]
    while stack:
        label = stack.pop()
        if (children := successors[label]):
            if len(children) == 1 and children - heads:
                [child] = children
                if len(predecessors[child]) == 1:
                    segment.append(label)
                    stack.append(child)
                    continue

            segment_roots.update(children - heads)

    changed = True

    def bubble_statements(label: CFG.BlockLabel, parent_writes: set[common.Variable], succession: list[CFG.BlockLabel]) -> list[CFG.Statement]:
        nonlocal root, graph, changed

        block = graph.blocks[label]
        total_writes = set()
        to_push = []
        if label == root:
            for statement in block.statements:
                match statement:
                    case CFG.Assignment(variable, _):
                        total_writes.add(variable)
        else:
            for i, statement in enumerate(block.statements):
                match statement:
                    case CFG.Emit(common.Expression(_, free_variables)):
                        if parent_writes.isdisjoint(free_variables):
                            to_push.append(i)
                    case CFG.Assignment(variable, common.Expression(_, free_variables)):
                        if parent_writes.isdisjoint({variable} | set(free_variables)):
                            to_push.append(i)
                        else:
                            total_writes.add(variable)

        to_push = [
            block.statements.pop(i)
            for i in to_push[::-1]
        ]

        if succession:
            child = succession.pop(0)
            pushed = bubble_statements(child, total_writes, succession)
            block.statements.extend(pushed)

        if to_push:
            changed = True

        return to_push

    while changed:
        changed = False
        bubble_statements(root, set(), segment[1:])

    return segment_roots


def conditional_variables(terminal: CFG.Terminal) -> set[common.Variable]:
    match terminal:
        case CFG.If(variable, truthy, falsey):
            truthy = conditional_variables(truthy)
            falsey = conditional_variables(falsey)
            return {variable} | truthy | falsey
        case _:
            return set()


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
    successors = label_graph(graph)
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
        if label in seen:
            return
        seen.add(label)

        n_parameters = len(parameters[label])
        successor_parameters = set()
        for successor in successors[label]:
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


def generate_pdg_annotations(graph: CFG.Graph[E, T], heads: set[CFG.BlockLabel]) -> CFG.Graph[E, T]:

    def walk(label: CFG.BlockLabel, terminal: CFG.Terminal, predicate: CFG.Predicate):
        nonlocal graph

        match terminal:
            case CFG.GoTo(target, arguments):
                graph.blocks[target].predecessor_references.append(CFG.FromBlock(
                    label=label,
                    arguments=arguments,
                    predicate=predicate
                ))
            case CFG.Jump(target, arguments):
                graph.jumps.append(CFG.JumpDirective(
                    origin=label,
                    destination=target,
                    parameters=arguments,
                    predicate=predicate
                ))
            case CFG.If(conditional, truthy_branch, falsey_branch):
                walk(label, truthy_branch, CFG.And(predicate, CFG.Variable(conditional)))
                walk(label, falsey_branch, CFG.And(predicate, CFG.Not(CFG.Variable(conditional))))

    for label in heads:
        graph.blocks[label].predecessor_references.append(CFG.FromLoop(expected_label=label))

    for label, block in graph.blocks.items():
        walk(label, block.terminal, CFG.Tautology())

    return graph


def fill_dummy_inputs(graph: CFG.Graph[E, T], dummy: E) -> CFG.Graph[E, T]:
    for parameter in graph.blocks[graph.entry_label].parameters:
        if parameter not in graph.inputs:
            graph.inputs[parameter] = common.Expression(dummy, [])
    return graph
