from textwrap import dedent

from .. import CFP
from ...library import utils


def pretty(primitive: CFP.Primitive) -> str:
    match primitive:
        case CFP.Emit(variables):
            return "EMIT " + ", ".join(
                variable.identifier for variable in variables
            )

        case CFP.Assignment(bindings):
            return "LET " + ",\n    ".join(
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
                    " " * (7 + len(variable.identifier)),
                )
                for variable, expression in bindings.items()
            )

        case CFP.Fork(variables, expression):
            this = f"FORK {','.join(variable.identifier for variable in variables)} = "
            this += utils.indent1(
                dedent(
                    expression.source.replace("\\", "\\\\").format(
                        *(
                            f"{{{argument.identifier}}}"
                            for argument in expression.arguments
                        )
                    )
                ),
                " " * len(this),
            )
            return this

        case CFP.Gather(aggregates, keys):
            this = "GATHER "
            this += ",\n       ".join(
                variable.identifier
                + " = "
                + utils.indent1(
                    dedent(
                        expression.source.replace("\\", "\\\\").format(
                            *(
                                f"{{{argument.identifier}}}"
                                for argument in expression.arguments
                            )
                        )
                    ),
                    " " * (10 + len(variable.identifier)),
                )
                for variable, expression in aggregates.items()
            )
            if keys:
                this += (
                    f"\nBY {','.join(variable.identifier for variable in keys)}"
                )
            return this

        case CFP.IsSynced(variable, label, keys):
            this = "LET " + variable.identifier + " = ALL "
            if keys:
                this += ",".join(variable.identifier for variable in keys) + " "
            this += "AT " + label.identifier
            return this

        case CFP.Where(variable, inverted):
            return f"WHERE {inverted * 'NOT '}{variable.identifier}"

        case CFP.Jump(label):
            return f"JUMP {label.identifier}"

        case _:
            return type(primitive).__name__.upper()
