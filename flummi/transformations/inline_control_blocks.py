from dataclasses import replace
from typing import TypeVar

from ..grammars import CFG, common
from ..algorithms import compute_dominator_tree


__all__ = (
    "inline_control_blocks",
)


E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


def inline_control_blocks(graph: CFG.Graph[E, T]) -> CFG.Graph[E, T]:
    changed = True
    while changed:
        dom = compute_dominator_tree(graph)
        changed = False
        for label, inlinee_block in graph.blocks.items():
            if not inlinee_block.statements:
                for inlineable in dom[label] - {label}:
                    block = graph.blocks[inlineable]
                    block.terminal, _changed = inline_terminal(block.terminal, label, inlinee_block.terminal)
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
