from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..solver import Dataflow
from ...IR import CFP
from ...library import sql


GENERATORS: dict[str, type[Generator]] = {}


@dataclass
class Generator(ABC):
    def __init_subclass__(cls, name: str = "") -> None:
        GENERATORS[name or cls.__name__] = cls

    dataflow: Dataflow

    @abstractmethod
    def generate_program(self, program: CFP.Program) -> sql.SQL:
        raise NotImplementedError
