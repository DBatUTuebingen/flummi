from ..IR.CFP import (
    Label,
    Program,
    Start,
)
from ..IR.common import Type
from .analysis import AnalysisResult
from .names import SystemVariable
from .solving import DataflowResult

__all__ = ("scheme",)


type Column = str
type Schema = dict[Column, Type]


def scheme(
    program: Program,
    analysis: AnalysisResult,
    data_flow: DataflowResult,
) -> Schema:
    labels_to_scheme: list[Label] = [
        label
        for label, primitive in program.body.primitives.items()
        if isinstance(primitive, Start)
    ]

    SYSTEM_SCHEMA = {
        variable.identifier: analysis.symbol_table[variable]
        for variable in analysis.system_variables.values()
        if variable.identifier
        not in {SystemVariable.CONTROL, SystemVariable.PROBE}
    }

    schema = SYSTEM_SCHEMA
    for label in labels_to_scheme:
        schema |= {
            input.identifier: analysis.symbol_table[input]
            for input in data_flow.inputs_of[label]
        }

    return schema
