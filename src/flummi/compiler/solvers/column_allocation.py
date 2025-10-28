from collections import defaultdict
from dataclasses import dataclass, field

from ...IR import CFP, common
from ...library import utils
from ..analyzer import SymbolTable
from .. import constants

__all__ = ("allocate_columns",)


type Column = str
type Schema = dict[Column, common.Type]
type Allocations = CFP.PerLabel[Allocation]


@dataclass(slots=True)
class Allocation:
    _variable_allocation: dict[CFP.Variable, Column]
    _column_allocation: dict[Column, CFP.Variable] = field(init=False)

    def __post_init__(self):
        self._column_allocation = {
            column: variable
            for variable, column in self._variable_allocation.items()
        }

    def column_for(self, variable: CFP.Variable) -> Column | None:
        return self._variable_allocation.get(variable)

    def variable_at(self, column: Column) -> CFP.Variable | None:
        return self._column_allocation.get(column)


def allocate_columns(
    labels_to_allocate: list[CFP.Label],
    symbol_table: SymbolTable,
    system_variables: dict[constants.Names, CFP.Variable],
    variables_at: CFP.PerLabel[set[CFP.Variable]],
) -> tuple[Schema, Allocations]:
    SYSTEM_SCHEMA = {
        variable.identifier: symbol_table[variable]
        for variable in system_variables.values()
    }

    # First, collect all "type siblings", i.e., groupings of like typed
    # variables, at each label we wish to perform column allocation for.
    # Since we are only looking at nodes containing start primitives, we
    # compute these type siblings over the inputs of the nodes. In addition
    # to the sets of type siblings themselves, we also collect the maximum
    # cardinality of them by type.

    type_siblings_at: CFP.PerLabel[dict[common.Type, list[CFP.Variable]]] = (
        defaultdict(lambda: defaultdict(list))
    )
    max_type_counts: dict[common.Type, int] = defaultdict(int)

    for label in labels_to_allocate:
        for type, variables in utils.groupby(
            iter(variables_at[label] - set(system_variables.values())),
            lambda variable: symbol_table[variable],
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
    offset_of: dict[common.Type, int] = {}
    for type, count in max_type_counts.items():
        offset_of[type] = offset
        schema.update(
            {
                constants.Names.PROGRAM.format(idx=offset + i): type
                for i in range(count)
            }
        )
        offset += count

    # Lastly, we compute the allocations for each label based on the schema
    # we determined above. (The reverse mappings are generated automatically
    # elsewhere, thus we can focus on simply computing on direction here.)

    allocations = {
        label: Allocation(
            {system_variables[constants.Names.LABEL]: constants.Names.LABEL}
            | {
                variable: constants.Names.PROGRAM.format(
                    idx=offset_of[type] + i
                )
                for type, variables in type_siblings_at.get(label, {}).items()
                for i, variable in enumerate(variables)
            }
        )
        for label in labels_to_allocate
    }

    return schema, allocations
