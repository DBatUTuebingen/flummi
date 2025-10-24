from enum import StrEnum

from .base import BACKENDS as _BACKENDS
from ..analyzer import SymbolTable
from ..constants import Names
from ..features import Feature
from ...IR import CFP
from ...library import sql, errors

# We disable the reporting of "unused" imports here, as we're importing these
# modules as a way method to dispatch their evaluation. Those evaluations
# automatically populate the BACKENDS dictionary, from which we can access
# the actual code generators!
from . import (
    cte,  # pyright: ignore[reportUnusedImport]  # noqa: F401
    lateral,  # pyright: ignore[reportUnusedImport]  # noqa: F401
    guarded_lateral,  # pyright: ignore[reportUnusedImport]  # noqa: F401
    apfel,  # pyright: ignore[reportUnusedImport]  # noqa: F401
    recursive_cte,  # pyright: ignore[reportUnusedImport]  # noqa: F401
    mutually_recursive_cte,  # pyright: ignore[reportUnusedImport]  # noqa: F401
)


__all__ = ("Backend",)


class FeatureError(ValueError, errors.PrettyError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


Backend = StrEnum("Backend", zip(_BACKENDS, _BACKENDS))


def run(
    backend: Backend,
    program: CFP.Program,
    features: dict[Feature, list[errors.Location | None]],
    symbol_table: SymbolTable,
    system_variables: dict[Names, CFP.Variable],
) -> sql.SQL:
    backend_cls = _BACKENDS[backend.value]

    unsupported_features = features.keys() - backend_cls.supported_features
    if unsupported_features:
        raise FeatureError(
            f"Program uses features the {backend.name!r} backend does not support: ",
            "",
            *sum(
                (
                    [
                        f"- {unsupported_feature.name.lower()}, found at:",
                        *sum(
                            (
                                [location, ""]
                                for location in features[unsupported_feature]
                                if location is not None
                            ),
                            start=list[errors.Reason](),
                        ),
                        "",
                    ]
                    for unsupported_feature in unsupported_features
                ),
                start=list[errors.Reason](),
            )[:-1],
        )

    return backend_cls(program, symbol_table, system_variables).generate()
