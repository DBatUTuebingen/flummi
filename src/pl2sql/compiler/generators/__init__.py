from enum import StrEnum

from .base import GENERATORS as _GENERATORS
from ..solver import FlowSolution
from ...IR import CFP
from ...library import sql

# We disable the reporting of "unused" imports here, as we're importing these
# modules as a way method to dispatch their evaluation. Those evaluations
# automatically populate the GENERATORS dictionary, from which we can access
# the actual code generators!
from . import cte, lateral, guarded_lateral  # pyright: ignore[reportUnusedImport]  # noqa: F401


__all__ = ("generate", "GenerationMethod")


GenerationMethod = StrEnum("GenerationMethod", zip(_GENERATORS, _GENERATORS))


def generate(
    method: GenerationMethod, program: CFP.Program, dataflow: FlowSolution
) -> sql.SQL:
    return _GENERATORS[method.value](dataflow).generate_program(program)
