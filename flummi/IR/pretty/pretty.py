from textwrap import indent, dedent

from .. import CFG
from ...library import utils


def pretty(node: CFG.Node) -> str:
    match node:
        case CFG.Emits(emits):
            return "\n".join(
                f"EMIT {",".join(
                    variable.identifier
                    for variable in emit.variables
                )}"
                for emit in emits
            )

        case CFG.Assignments(assignments):
            formatted = []
            for assignment in assignments:
                this = "LET "
                this += ",".join(
                    variable.identifier
                    for variable in assignment.variables
                ) + " = (\n"
                this += indent(dedent(assignment.expression.source), ' ' * 2)
                this += f"\n)[{", ".join(
                    argument.identifier
                    for argument in  assignment.expression.arguments
                )}]"
                formatted.append(this)
            return "\n".join(formatted)

        case CFG.Join(variables, expression) | CFG.Fork(variables, expression):
            match node:
                case CFG.Join():
                    this = "JOIN "
                case CFG.Fork():
                    this = "FORK "
            this += ",".join(
                variable.identifier
                for variable in variables
            ) + " = (\n"
            this += indent(dedent(expression.source), ' ' * 2)
            this += f"\n)[{", ".join(
                argument.identifier
                for argument in  expression.arguments
            )}]"
            return this

        case CFG.Source(label):
            return f"SOURCE {label.identifier}"

        case CFG.Sink(label):
            return f"SINK {label.identifier}"

        case CFG.Conditional(truthy, falsey):
            conjuncts = [
                variable.identifier
                for variable in truthy
            ] + [
                f"NOT {variable.identifier}"
                for variable in falsey
            ]

            return f"FILTER (\n{indent("\n".join(conjuncts), ' ' * 2)}\n)"

        case _:
            return type(node).__name__.upper()
