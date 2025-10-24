from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from inspect import isabstract
from typing import ClassVar

from ..features import Features
from ..analyzer import SymbolTable
from ..constants import Names
from ...IR import CFP
from ...library import sql, errors
from ..solvers.live_variable_analysis import (
    InputMap,
    OutputMap,
    analyze_live_variables,
)
from ..solvers.column_allocation import Schema, Allocations, allocate_columns
from ..solvers.reaching_definitions_analysis import (
    Definitions,
    analyze_reaching_definitions,
)
from ..solvers.region_guard_analysis import Guard, Region, analyze_region_guards


class GenerationError(errors.PrettyError, ValueError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


BACKENDS: dict[str, type[Backend]] = {}  # noqa: F821  <-- no python 3.14 support yet...


@dataclass
class Backend(ABC):
    def __init_subclass__(
        cls, supports: Features = Features.SEQUENCING, name: str = ""
    ) -> None:
        if not isabstract(cls):
            BACKENDS[name or cls.__name__] = cls
        cls.supported_features = supports

    supported_features: ClassVar[Features]

    program: CFP.Program
    symbol_table: SymbolTable
    system_variables: dict[Names, CFP.Variable]

    def __post_init__(self): ...

    @abstractmethod
    def generate(self) -> sql.SQL:
        raise NotImplementedError


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
    definitions_after: dict[CFP.Label, Definitions] = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self.definitions_after = analyze_reaching_definitions(
            self.program,
        )


@dataclass
class UseGuards(Backend, ABC):
    guard_of: dict[CFP.Label, Guard] = field(init=False)
    guarded_by: dict[Guard, Region] = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self.guard_of, self.guarded_by = analyze_region_guards(
            self.program,
        )


@dataclass
class PrimitiveBackend(Backend, ABC):
    @abstractmethod
    def generate_primitive(
        self,
        label: CFP.Label,
        primitive: CFP.Primitive,
        predecessors: set[CFP.Label],
    ) -> sql.SQL:
        raise GenerationError(
            f"This generator does not support {type(primitive).__name__} primitives.",
            "This primitive comes from here...",
            primitive.location,
        )
