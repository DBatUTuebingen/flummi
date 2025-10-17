from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from inspect import isabstract

from ..solver import FlowSolution
from ...IR import CFP
from ...library import sql, errors


class GenerationError(errors.PrettyError, ValueError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


GENERATORS: dict[str, type[Generator]] = {}


@dataclass
class Generator(ABC):
    def __init_subclass__(cls, name: str = "") -> None:
        if not isabstract(cls):
            GENERATORS[name or cls.__name__] = cls

    program: CFP.Program
    flow: FlowSolution

    @abstractmethod
    def generate(self) -> sql.SQL:
        raise NotImplementedError


class PrimitiveGenerator(Generator, ABC):
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
