from collections import defaultdict
from dataclasses import dataclass, field

from ..IR.CFP import (
    Label,
    Program,
    Start,
    Variable,
)
from ..IR.common import Type
from ..library import utils
from .analysis import AnalysisResult
from .names import PROGRAM_VARIABLE, SystemVariable
from .solving import DataflowResult

__all__ = ("allocate",)


type Column = str
type Schema = dict[Column, Type]

type PerLabel[T] = dict[Label, T]


@dataclass(slots=True)
class Allocation:
    _variable_allocation: dict[Variable, Column]
    _column_allocation: dict[Column, Variable] = field(init=False)

    def __post_init__(self):
        self._column_allocation = {
            column: variable
            for variable, column in self._variable_allocation.items()
        }

    def column_for(self, variable: Variable) -> Column | None:
        return self._variable_allocation.get(variable)

    def variable_at(self, column: Column) -> Variable | None:
        return self._column_allocation.get(column)


@dataclass(frozen=True, slots=True)
class AllocationResult:
    schema: Schema
    at: PerLabel[Allocation]


def allocate(
    program: Program,
    analysis: AnalysisResult,
    data_flow: DataflowResult,
) -> AllocationResult:
    labels_to_allocate: list[Label] = [
        label
        for label, primitive in program.body.primitives.items()
        if isinstance(primitive, Start)
    ]

    SYSTEM_SCHEMA = {
        variable.identifier: analysis.symbol_table[variable]
        for variable in analysis.system_variables.values()
        if variable.identifier != SystemVariable.CONTROL
    }

    # First, collect all "type siblings", i.e., groupings of like typed
    # variables, at each label we wish to perform column allocation for.
    # Since we are only looking at nodes containing start primitives, we
    # compute these type siblings over the inputs of the nodes. In addition
    # to the sets of type siblings themselves, we also collect the maximum
    # cardinality of them by type.

    type_siblings_at: PerLabel[dict[Type, list[Variable]]] = defaultdict(
        lambda: defaultdict(list)
    )
    max_type_counts: dict[Type, int] = defaultdict(int)

    for label in labels_to_allocate:
        for type, variables in utils.groupby(
            iter(
                data_flow.inputs_of[label]
                - set(analysis.system_variables.values())
            ),
            lambda variable: analysis.symbol_table[variable],
        ):
            variables = list(variables)
            type_siblings_at[label][type] = variables
            count = len(variables)
            if count > max_type_counts[type]:
                max_type_counts[type] = count

    # Second, we compute the schema of the working table in two parts. The
    # first part simply contains the system columns, e.g. the column for
    # goto targets, the one for program results etc. The second part,
    # contains the program columns, i.e., this set contains just enough
    # columns of each type, such that all sets of type siblings computed
    # above are covered.

    schema: Schema = dict(SYSTEM_SCHEMA)
    offset: int = 0
    offset_of: dict[Type, int] = {}
    for type, count in max_type_counts.items():
        offset_of[type] = offset
        schema.update(
            {
                PROGRAM_VARIABLE.format(idx=offset + i): type
                for i in range(count)
            }
        )
        offset += count

    # Lastly, we compute the allocations for each label based on the schema
    # we determined above. (The reverse mappings are generated automatically
    # elsewhere, thus we can focus on simply computing on direction here.)

    allocations: dict[Label, Allocation] = {
        label: Allocation(
            {
                analysis.system_variables[
                    SystemVariable.LABEL
                ]: SystemVariable.LABEL,
            }
            | {
                variable: PROGRAM_VARIABLE.format(idx=offset_of[type] + i)
                for type, variables in type_siblings_at.get(label, {}).items()
                for i, variable in enumerate(variables)
            }
        )
        for label in labels_to_allocate
    }

    return AllocationResult(schema, allocations)
