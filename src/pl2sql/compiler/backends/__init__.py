from enum import StrEnum

from .base import BACKENDS as _BACKENDS
from ..analyzer import SymbolTable
from ..constants import Names
from ..features import Features
from ...IR import CFP
from ...library import sql, errors

# We disable the reporting of "unused" imports here, as we're importing these
# modules as a way method to dispatch their evaluation. Those evaluations
# automatically populate the BACKENDS dictionary, from which we can access
# the actual code generators!
from . import cte, lateral, guarded_lateral, apfel, recursive_cte  # pyright: ignore[reportUnusedImport]  # noqa: F401


__all__ = ("Backend",)


class FeatureError(ValueError, errors.PrettyError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


Backend = StrEnum("Backend", zip(_BACKENDS, _BACKENDS))


def run(
    backend: Backend,
    program: CFP.Program,
    features: Features,
    symbol_table: SymbolTable,
    system_variables: dict[Names, CFP.Variable],
) -> sql.SQL:
    backend_cls = _BACKENDS[backend.value]

    unsported_features = features & ~backend_cls.supported_features
    if unsported_features:
        raise FeatureError(
            "Program uses features the backend does not support: "
            + f"{','.join(str(feature.name) for feature in unsported_features)}."
        )

    return backend_cls(program, symbol_table, system_variables).generate()
