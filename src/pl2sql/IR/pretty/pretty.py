from textwrap import dedent

from .. import CFP
from ...library import utils


def pretty(node: CFP.Node) -> str:
    match node:
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

        case _:
            return type(node).__name__.upper()
