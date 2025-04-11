from textwrap import dedent

from .. import CFG
from ...library import utils


def pretty(node: CFG.Node) -> str:
    match node:
        case CFG.Emit(function, variable):
            return f"EMIT {variable.identifier} FROM {function.identifier}"

        case CFG.Let(variable, expression):
            this = f"LET {variable.identifier} = "
            this += utils._indent(dedent(expression.source.format(*(
                f"{{{argument.identifier}}}"
                for argument in  expression.arguments
            ))), ' ' * len(this))
            return this

        case CFG.Pop(label):
            return f"POP {label.identifier}"

        case CFG.Push(label):
            return f"PUSH {label.identifier}"

        case CFG.Where(variable):
            return f"WHERE {variable.identifier}"

        case CFG.WhereNot(variable):
            return f"WHERE NOT {variable.identifier}"

        case CFG.Merge():
            return "MERGE"

        case CFG.Link(label):
            return f"LINK {label.identifier}"

        case CFG.Resume(function, variable):
            return f"RESUME {function.identifier} AS {variable.identifier}"

        case CFG.Lookup(result, hit, function, arguments):
            pretty_arguments = ", ".join(
                f"{parameter.identifier}: {argument.identifier}"
                for parameter, argument in arguments.items()
            )
            return f"LOOKUP {result.identifier}, {hit.identifier} = {function.identifier}({pretty_arguments})"

        case CFG.Memoize(function, arguments, result):
            pretty_arguments = ", ".join(
                f"{parameter.identifier}: {argument.identifier}"
                for parameter, argument in arguments.items()
            )
            return f"MEMOIZE {function.identifier}({pretty_arguments}) = {result.identifier}"

        case _:
            return type(node).__name__.upper()
