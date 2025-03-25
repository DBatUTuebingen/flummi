from dataclasses import dataclass
import itertools

from . import names
from .analyzer import SymbolTable
from ..IR import CFG, AST, common
from ..library import utils


def plan_data_flow[A](ast: AST.Program[A], cfg: CFG.Graph[A], symbol_table: SymbolTable):
    inputs = get_block_inputs(cfg)
    outputs = get_block_outputs(cfg, inputs)

    #! [todo] do proper! these are just lazy options
    registers = {
        variable.identifier: (
            common.Type("INT", annotation=ast.annotation)
            if variable.identifier in {names.depth, names.iteration} else
            common.Type("TEXT", annotation=ast.annotation)
            if variable.identifier in {names.label,names.return_label} else
            common.Type("TEXT", annotation=ast.annotation)
            if variable.identifier == names.kind else
            symbol_table[variable]
        )
        for label, node in cfg.nodes.items()
        if isinstance(node, CFG.Pop)
        for variable in outputs[label]
    } | {
        RESULT(function.name, function.annotation).identifier: function.return_type
        for function in ast.function_list
    }

    variable_allocations = {}
    register_allocations = {}

    for label, node in cfg.nodes.items():
        if isinstance(node, CFG.Pop):
            variable_allocation = {}
            register_allocation = {}

            for variable in outputs[label]:
                variable_allocation[variable] = variable.identifier
                register_allocation[variable.identifier] = variable

            variable_allocations[node.label] = variable_allocation
            register_allocations[node.label] = register_allocation

    result_allocation = {
        function.name: RESULT(function.name, function.annotation).identifier
        for function in ast.function_list
    } | {
        None: "@result"
    }

    return outputs, registers, variable_allocations, register_allocations, result_allocation


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
                    if isinstance(successor, CFG.Pop)
                    and successor.label == node.label
                ) if isinstance(node, CFG.Push) else ()
            )
        )
        for label, node in cfg.nodes.items()
    }

def free_variables[A](node: CFG.Node[A]) -> set[common.Identifier[A]]:
    match node:
        case CFG.Let(_, common.Expression(_, variables)):
            return set(variables)

        case CFG.Return(_, variable):
            return {
                variable,
                RETURN_LABEL(node.annotation),
                DEPTH(node.annotation),
                ITERATION(node.annotation),
            }

        case CFG.Where(variable) | CFG.WhereNot(variable):
            return {variable}

        case CFG.Push():
            return {
                RETURN_LABEL(node.annotation),
                DEPTH(node.annotation),
                ITERATION(node.annotation),
            }

        case CFG.Link():
            return {
                DEPTH(node.annotation),
            }

        case CFG.Resume():
            return {
                LABEL(node.annotation),
                DEPTH(node.annotation),
            }

        case CFG.Memoize(_, arguments, variable):
            return {variable, *arguments.values()}

        case CFG.Lookup(_, _, _, arguments):
            return set(arguments.values())

        case _:
            return set()

def bound_variables[A](node: CFG.Node[A]) -> set[common.Identifier[A]]:
    match node:
        case CFG.Pop():
            return {
                LABEL(node.annotation),
                RETURN_LABEL(node.annotation),
                DEPTH(node.annotation),
                ITERATION(node.annotation),
            }

        case CFG.Resume(_, variable) | CFG.Let(variable, _):
            return {variable}

        case CFG.Link():
            return {
                RETURN_LABEL(node.annotation),
                DEPTH(node.annotation),
            }

        case CFG.Lookup(result, hit, _):
            return {result, hit}

        case _:
            return set()


def ITERATION(annotation): return common.Identifier(names.iteration, annotation=annotation)
def KIND(annotation): return common.Identifier(names.kind, annotation=annotation)
def LABEL(annotation): return common.Identifier(names.label, annotation=annotation)
def DEPTH(annotation): return common.Identifier(names.depth, annotation=annotation)
def RETURN_LABEL(annotation): return common.Identifier(names.return_label, annotation=annotation)
def RESULT(function: common.Identifier, annotation): return common.Identifier(f"{function.identifier}@result", annotation=annotation)
