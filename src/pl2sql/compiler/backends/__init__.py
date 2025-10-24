from enum import StrEnum

from .base import BACKENDS as _BACKENDS
from ..analyzer import SymbolTable
from ..constants import Names
from ...IR import CFP
from ...library import sql

# We disable the reporting of "unused" imports here, as we're importing these
# modules as a way method to dispatch their evaluation. Those evaluations
# automatically populate the BACKENDS dictionary, from which we can access
# the actual code generators!
from . import cte, lateral, guarded_lateral, apfel, recursive_cte  # pyright: ignore[reportUnusedImport]  # noqa: F401


__all__ = ("Backend",)


Backend = StrEnum("Backend", zip(_BACKENDS, _BACKENDS))


def run(
    backend: Backend,
    program: CFP.Program,
    symbol_table: SymbolTable,
    system_variables: dict[Names, CFP.Variable],
) -> sql.SQL:
    return _BACKENDS[backend.value](
        program, symbol_table, system_variables
    ).generate()
