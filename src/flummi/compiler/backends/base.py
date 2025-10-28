from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from inspect import isabstract
from typing import ClassVar

from ..features import Features, MINIMAL_FEATURES
from ..analyzer import SymbolTable
from ..constants import Names
from ...IR import CFP
from ...library import sql, errors, graph


class GenerationError(errors.PrettyError, ValueError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


BACKENDS: dict[str, type[Backend]] = {}  # noqa: F821  <-- no python 3.14 support yet...


@dataclass
class Backend(ABC):
    def __init_subclass__(
        cls,
        supports: Features = MINIMAL_FEATURES,
        name: str = "",
        *args,  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        **kwargs,  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    ) -> None:
        super().__init_subclass__(*args, **kwargs)

        if not isabstract(cls):
            BACKENDS[name or cls.__name__] = cls
        cls.supported_features = supports

    supported_features: ClassVar[Features]

    program: CFP.Program
    symbol_table: SymbolTable
    system_variables: dict[Names, CFP.Variable]

    primitives: dict[CFP.Label, CFP.Primitive] = field(init=False)

    successors_of: dict[CFP.Label, set[CFP.Label]] = field(init=False)
    predecessors_of: dict[CFP.Label, set[CFP.Label]] = field(init=False)

    virtual_successors_of: dict[CFP.Label, set[CFP.Label]] = field(init=False)
    virtual_predecessors_of: dict[CFP.Label, set[CFP.Label]] = field(init=False)

    def __post_init__(self):
        self.primitives = self.program.body.primitives

        self.successors_of = self.program.body.direct_edges
        self.predecessors_of = graph.invert(self.successors_of)

        self.virtual_successors_of = graph.merge(
            self.program.body.direct_edges, self.program.body.indirect_edges
        )
        self.virtual_predecessors_of = graph.invert(self.virtual_successors_of)

    @abstractmethod
    def generate(self) -> sql.SQL:
        raise NotImplementedError


@dataclass
class PrimitiveBackend(Backend, ABC):
    @abstractmethod
    def generate_primitive(
        self,
        label: CFP.Label,
    ) -> sql.SQL:
        primitive = self.primitives[label]
        raise GenerationError(
            f"This generator does not support {type(primitive).__name__} primitives.",
            "This primitive comes from here...",
            primitive.location,
        )
