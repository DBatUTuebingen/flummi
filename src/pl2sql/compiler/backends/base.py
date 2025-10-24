from abc import ABC, abstractmethod
from dataclasses import dataclass
from inspect import isabstract
from typing import ClassVar

from ..features import Features, MINIMAL_FEATURES
from ..analyzer import SymbolTable
from ..constants import Names
from ...IR import CFP
from ...library import sql, errors


class GenerationError(errors.PrettyError, ValueError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


BACKENDS: dict[str, type[Backend]] = {}  # noqa: F821  <-- no python 3.14 support yet...


@dataclass
class Backend(ABC):
    def __init_subclass__(
        cls,
        supports: Features = MINIMAL_FEATURES,
        name: str = "",
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
