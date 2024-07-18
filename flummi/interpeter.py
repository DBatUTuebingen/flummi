from typing import Any, Iterator

import duckdb

from .IR import AST
from .library import errors, sql
from .compiler import parser


__all__ = (
    "interpret",
)


class EvaluationError(errors.PrettyError, RuntimeError):
    ...


def interpret(
    program: parser.Program,
    symbol_table: dict[parser.Identifier, parser.Type],
    statement: parser.Statement | None = None,
    environment: dict[str, Any] | None = None,
) -> Iterator[tuple[Any, ...]]:
    environment = environment or {}

    if statement is None:
        if program.inputs is not None:
            statement = AST.Block(
                [
                    AST.Assignment(
                        list(program.main_function.parameters.keys()),
                        program.inputs,
                        annotation=program.inputs.annotation,
                    ),
                    program.main_function.body
                ],
                annotation=program.annotation,
            )
        else:
            statement = program.main_function.body

    query_cache: dict[errors.Location, str] = {}
    stack: list[AST.Statement] = [statement]

    while stack:
        statement = stack.pop()

        match statement:
            case AST.Stop():
                return

            case AST.NoOp():
                ...

            case AST.Block(statements):
                stack.extend(statements[::-1])

            case AST.Emit(variables):
                yield tuple(
                    environment[variable.identifier]
                    for variable in variables
                )

            case AST.If(condition, t_branch, f_branch):
                choice = environment[condition.identifier]
                if not isinstance(choice, bool):
                    raise EvaluationError(
                        "Condition is non-boolean.",
                        condition.annotation,
                        "",
                        "Current scope:",
                        *(
                            f"{variable} := {value!r}"
                            for variable, value in environment.items()
                        ),
                    ) from TypeError()
                stack.append(t_branch if choice else f_branch)

            case AST.Loop(name, body):
                stack.append(statement)
                stack.append(body)

            case AST.Continue(name) | AST.Break(name):
                while stack:
                    next = stack.pop()
                    match next:
                        case AST.Loop(_name, body) if name == _name:
                            if isinstance(statement, AST.Continue):
                                stack.append(next)
                            break
                else:
                    ...

            case AST.Assignment(variables, expression):
                if expression.annotation not in query_cache:
                    try:
                        query = sql.select(
                            select_list=[
                                sql.cast(
                                    sql.variable(variable.identifier, row="_"),
                                    symbol_table[variable].source
                                )
                                for variable in variables
                            ],
                            from_list=[
                                sql.named(
                                    sql.paren(
                                        (
                                            expression.source
                                            if len(variables) > 1 else
                                            f"SELECT ({expression.source})"
                                        ).format(*(
                                            f"(${i+1} :: {symbol_table[free_variable].source})"
                                            for i, free_variable in enumerate(expression.arguments)
                                        ))
                                    ),
                                    name = "_",
                                    columns=[
                                        variable.identifier
                                        for variable in variables
                                    ]
                                )
                            ]
                        )
                    except Exception as e:
                        raise EvaluationError(
                            "Encountered an error during formatting of an "
                            "embedded SQL expression.",
                            expression.annotation,
                            "",
                            "Given Query:",
                            expression.source,
                            "",
                            "Current scope:",
                            *(
                                f"{variable} := {value!r}"
                                for variable, value in environment.items()
                            ),
                            "",
                            "Error:",
                            repr(e)
                        ) from e

                    query_cache[expression.annotation] = query
                else:
                    query = query_cache[expression.annotation]
                parameters = [
                    environment[free_variable.identifier]
                    for free_variable in expression.arguments
                ]
                try:
                    row = duckdb.execute(query, parameters).fetchone()
                except Exception as e:
                    raise EvaluationError(
                        "Encountered an error during evaluation of an "
                        "embedded SQL expression.",
                        expression.annotation,
                        "",
                        "Executed Query:",
                        query,
                        "",
                        "Current scope:",
                        *(
                            f"{variable} := {value!r}"
                            for variable, value in environment.items()
                        ),
                        "",
                        "Error:",
                        str(e)
                    ) from e

                if row is None:
                    raise EvaluationError(
                        "Embedded SQL expression produced no output.",
                        expression.annotation,
                        "",
                        "Current scope:",
                        *(
                            f"{variable} := {value!r}"
                            for variable, value in environment.items()
                        ),
                    )

                environment.update(
                    (variable.identifier, value)
                    for variable, value in zip(variables, row)
                )

            case _:
                raise EvaluationError(
                    "Encountered unsupported statement.",
                    statement.annotation
                )

    raise EvaluationError(
        "Ran out of things to do before expecting it...",
        program.annotation,
    )
