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

        case CFP.Fork(variables, expression):
            this = f"FORK {', '.join(variable.identifier for variable in variables)} = "
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

        case CFP.SiblingProbe(variable, label, keys):
            this = f"PROBE {variable.identifier} = ALL SIBLINGS AT {label.identifier}"
            if keys:
                this += f" KEYS ({', '.join(variable.identifier for variable in keys)})"
            return this

        case CFP.Gather(aggregates, keys):
            this = "GATHER "
            this += (",\n" + " " * len(this)).join(
                variable.identifier
                + " = "
                + utils.indent1(
                    dedent(
                        expression.source.format(
                            *(
                                f"{{{argument.identifier}}}"
                                for argument in expression.arguments
                            )
                        )
                    ),
                    " " * (len(this) + len(variable.identifier) + len(" = ")),
                )
                for variable, expression in aggregates.items()
            )
            this += f"\nBY {', '.join(key.identifier for key in keys)}"
            return this

        case _:
            return type(primitive).__name__.upper()
