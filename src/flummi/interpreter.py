from collections.abc import Iterator
from typing import Any

import duckdb

from .IR import common, AST
from .library import sql, errors


type Value = Any  # pyright: ignore[reportExplicitAny]


class EvaluationError(RuntimeError, errors.PrettyError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


def evaluate(
    program: AST.Program, symbol_table: dict[AST.Variable, common.Type]
) -> Iterator[Value]:
    environment: dict[AST.Variable, Value] = {}

    stack = [program.body]
    query_cache: dict[str, sql.SQL] = {}

    while stack:
        statement = stack.pop()

        match statement:
            case AST.NoOp():
                ...

            case AST.Declare(variable, type):
                symbol_table[variable] = type

            case AST.Let(variable, expression):
                if expression.source not in query_cache:
                    try:
                        query = sql.select(
                            select_list=[
                                sql.cast(
                                    expression.source.format(
                                        *(
                                            f"(${i + 1} :: {symbol_table[free_variable].source})"
                                            for i, free_variable in enumerate(
                                                expression.arguments
                                            )
                                        )
                                    ),
                                    symbol_table[variable].source,
                                )
                            ]
                        )
                    except Exception as e:
                        raise EvaluationError(
                            "Encountered an error during the formatting of an embedded SQL expression.",
                            expression.location,
                        ) from e
                    query_cache[expression.source] = query
                else:
                    query = query_cache[expression.source]

                parameters = [
                    environment[free_variable]
                    for free_variable in expression.arguments
                ]

                try:
                    row = duckdb.execute(query, parameters).fetchone()
                except Exception as e:
                    raise EvaluationError(
                        "Encountered an error during the evaluation of an embedded SQL expression.",
                        expression.location,
                    ) from e

                if row is None:
                    raise EvaluationError(
                        "Embedded SQL expression produced no output!",
                        expression.location,
                    )

                environment[variable] = row[0]

            case AST.Emit(variable):
                yield environment[variable]

            case AST.Stop():
                return

            case AST.Block(statements):
                stack.extend(statements[::-1])

            case AST.If(variable, truthy_branch, falsey_branch):
                match choice := environment[variable]:  # pyright: ignore[reportAny]
                    case bool():
                        stack.append(truthy_branch if choice else falsey_branch)

                    case _:  # pyright: ignore[reportAny]
                        raise EvaluationError(
                            "Encountered a non-boolean valued condition.",
                            statement.location,
                        )

            case AST.Loop(name, body):
                stack.append(statement)
                stack.append(body)

            case AST.Continue(name) | AST.Break(name):
                while stack:
                    next = stack.pop()
                    match next:  # pyright: ignore[reportMatchNotExhaustive]
                        case AST.Loop(loop_name, body) if loop_name == name:
                            if isinstance(statement, AST.Continue):
                                stack.append(next)
                            else:
                                break

            case _:
                raise EvaluationError(
                    f"{statement.__class__.__name__} statements not supported.",
                    statement.location,
                )
