from collections.abc import Iterator
from typing import Any

import duckdb

from .IR import AST

from . import errors, sql
from .pretty import pretty


__all__ = (
    "interpret",
)


class EvaluationError(errors.FlummiError, name="evaluation"):
    ...


def interpret(
    program: AST.Program,
    symbol_table: dict[AST.Variable, AST.Type],
    statement: AST.Statement | None = None,
    environment: dict[str, Any] | None = None,
) -> tuple[Any, ...]:
    environment = environment or {}

    if statement is None:
        if program.inputs is not None:
            statement = AST.Block(
                program.location,
                [
                    AST.Assignment(
                        program.inputs.location,
                        list(program.main_function.parameters.keys()),
                        program.inputs
                    ),
                    program.main_function.body
                ]
            )
        else:
            statement = program.main_function.body

    query_cache: dict[AST.Location, str] = {}
    stack: list[AST.Statement] = [statement]

    while stack:
        statement = stack.pop()

        match statement:
            case AST.NoOp():
                ...

            case AST.Block(_, statements):
                stack.extend(statements[::-1])

            case AST.Return(_, variables):
                return tuple(
                    environment[variable.identifier]
                    for variable in variables
                )

            case AST.If(_, condition, t_branch, f_branch):
                choice = environment[condition.identifier]
                if not isinstance(choice, bool):
                    raise EvaluationError(
                        "Condition is non-boolean.",
                        condition.location,
                        "",
                        "Current scope:",
                        *(
                            f"{variable} := {value!r}"
                            for variable, value in environment.items()
                        ),
                    )
                stack.append(t_branch if choice else f_branch)

            case AST.Loop(_, name, body):
                stack.append(statement)
                stack.append(body)

            case AST.Continue(_, name) | AST.Break(_, name):
                while stack:
                    next = stack.pop()
                    match next:
                        case AST.Loop(_, _name, body) if name == _name:
                            if isinstance(statement, AST.Continue):
                                stack.append(next)
                            break
                else:
                    ...

            case AST.Assignment(location, variables, expression):
                if location not in query_cache:
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
                                            for i, free_variable in enumerate(expression.free_variables)
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
                            expression.location,
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

                    query_cache[location] = query
                else:
                    query = query_cache[location]
                parameters = [
                    environment[free_variable.identifier]
                    for free_variable in expression.free_variables
                ]
                try:
                    row = duckdb.execute(query, parameters).fetchone()
                except Exception as e:
                    raise EvaluationError(
                        "Encountered an error during evaluation of an "
                        "embedded SQL expression.",
                        expression.location,
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
                        expression.location,
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

            case AST.Call(location, variables, function, arguments):
                function = program.functions[function]
                arguments = {
                    parameter.identifier:
                    environment[argument.identifier]
                    for parameter, argument in zip(
                        function.parameters,
                        arguments,
                    )
                }

                row = interpret(
                    program,
                    symbol_table,
                    statement=function.body,
                    environment=arguments
                )

                environment.update(
                    (variable.identifier, value)
                    for variable, value in zip(variables, row)
                )

            case _:
                raise EvaluationError(
                    "Encountered unsupported statement.",
                    statement.location
                )
    raise EvaluationError(
        "Ran out of things to do before expecting it...",
        program.location,
    )
