from typing import TypeVar

from ..grammars import CFG, common


__all__ = (
    "fill_dummy_inputs",
)


E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


def fill_dummy_inputs(graph: CFG.Graph[E, T], dummy: E) -> CFG.Graph[E, T]:
    for parameter in graph.blocks[graph.entry_label].parameters:
        if parameter not in graph.inputs:
            graph.inputs[parameter] = common.Expression(dummy, [])
    return graph
