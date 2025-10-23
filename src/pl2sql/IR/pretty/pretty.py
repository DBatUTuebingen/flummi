from textwrap import dedent

from .. import CFP
from ...library import utils


def pretty(primitive: CFP.Primitive) -> str:
    match primitive:
        case CFP.Emit(variable):
            return f"EMIT {variable.identifier}"

        case CFP.Let(variable, expression):
            this = f"LET {variable.identifier} = "
            this += utils.indent1(
                dedent(
                    expression.source.format(
                        *(
                            f"{{{argument.identifier}}}"
                            for argument in expression.arguments
                        )
                    )
                ),
                " " * len(this),
            )
            return this

        case CFP.Where(variable):
            return f"WHERE {variable.identifier}"

        case CFP.WhereNot(variable):
            return f"WHERE NOT {variable.identifier}"

        case CFP.GoTo(label):
            return f"GOTO {label.identifier}"

        case _:
            return type(primitive).__name__.upper()
