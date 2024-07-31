from textwrap import dedent

from .. import CFG
from ...library import utils


def pretty(node: CFG.Node) -> str:
    match node:
        case CFG.Emit(variables):
            return f"EMIT {",".join(
                variable.identifier
                for variable in variables
            )}"

        case CFG.Join(variables, expression) | CFG.Fork(variables, expression) | CFG.Assignment(variables, expression):
            match node:
                case CFG.Join():
                    this = "JOIN "
                case CFG.Fork():
                    this = "FORK "
                case CFG.Assignment():
                    this = "LET "
            this += ", ".join(
                variable.identifier
                for variable in variables
            ) + " = "
            this += utils._indent(dedent(expression.source.format(*(
                f"{{{argument.identifier}}}"
                for argument in  expression.arguments
            ))), ' ' * len(this))
            return this

        case CFG.Call(variables, function, arguments):
            variables = ", ".join(
                variable.identifier
                for variable in variables
            )
            arguments = ", ".join(
                argument.identifier
                for argument in arguments
            )
            return f"CALL {variables} = {function.identifier}({arguments})"

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

            return f"FILTER {utils._indent("\nAND".join(conjuncts), ' ' * 7)}"

        case _:
            return type(node).__name__.upper()
