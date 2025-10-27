from abc import ABC
from dataclasses import dataclass, field

from .base import Backend
from ..solvers.live_variable_analysis import (
    InputMap,
    OutputMap,
    analyze_live_variables,
)
from ..solvers.column_allocation import Schema, Allocations, allocate_columns
from ..solvers.reaching_definitions_analysis import (
    DefinitionMap,
    analyze_reaching_definitions,
)
from ..solvers.region_guard_analysis import (
    GuardMap,
    RegionMap,
    analyze_region_guards,
)


@dataclass
class UseLiveVariables(Backend, ABC):
    inputs_of: InputMap = field(init=False)
    outputs_of: OutputMap = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self.inputs_of, self.outputs_of = analyze_live_variables(
            self.program, self.system_variables
        )


@dataclass
class UseColumnAllocation(UseLiveVariables, ABC):
    schema: Schema = field(init=False)
    allocation_for: Allocations = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self.schema, self.allocation_for = allocate_columns(
            self.program,
            self.symbol_table,
            self.system_variables,
            self.inputs_of,
        )


@dataclass
class UseReachingDefinitions(Backend, ABC):
    definitions_after: DefinitionMap = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self.definitions_after = analyze_reaching_definitions(
            self.program,
        )


@dataclass
class UseGuards(Backend, ABC):
    guard_of: GuardMap = field(init=False)
    guarded_by: RegionMap = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self.guard_of, self.guarded_by = analyze_region_guards(
            self.program,
        )
