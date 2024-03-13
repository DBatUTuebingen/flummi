from __future__ import annotations
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from itertools import groupby as _groupby
from typing import Any, Callable

import pandas as pd
import duckdb

from . import grammar, errors

__all__ = (
    "interpret",
)


class EvaluationError(errors.FlummiError, name="Eval"):
    ...


def interpret(
    program: grammar.Program,
    symbol_table: dict[grammar.Variable, grammar.Type]
) -> Iterator[tuple[dict[str, Any], Iterator[Any]]]:
    yield from Interpreter(symbol_table).eval_program(program)


def groupby[T, K](
    things: Iterable[T],
    key: Callable[[T], K]
) -> Iterator[tuple[K, Iterable[T]]]:
    return _groupby(
        sorted(
            things,
            key=key  # type: ignore
        ),
        key=key
    )


def _stringify(things: Iterable[grammar.Variable]) -> list[str]:
    return [
        variable.identifier
        for variable in things
    ]


type Environment = dict[str, Any]


@dataclass(slots=True)
class Interpreter:
    symbol_table: dict[grammar.Variable, grammar.Type]
    results: list[Any] = field(init=False, default_factory=list)

    def eval_program(
        self,
        program: grammar.Program
    ) -> Iterator[tuple[dict[str, Any], Iterator[Any]]]:
        blank_state = dict.fromkeys(_stringify(self.symbol_table))
        if program.inputs is not None:
            duckdb.execute(program.inputs.source)
            results = duckdb.fetchall()
            if (
                program.inputs.valuedness == grammar.Valuedness.SCALAR and
                len(results) > 1
            ):
                raise EvaluationError(
                    "Expected expression to be scalar-valued "
                    "but it yielded a too many of results.",
                    program.inputs.location
                )
            elif len(results) == 0:
                raise EvaluationError(
                    "Expression produced no rows! "
                    "Can't call the function with no inputs...",
                    program.inputs.location
                )
            bindings = [
                dict(zip(
                    _stringify(program.function.parameters.keys()),
                    value
                ))
                for value in results
            ]
        else:
            bindings = [{}]

        for binding in bindings:
            self.results = []
            self.eval_statement(program.function.body, [blank_state | binding])
            yield binding, iter(self.results)

    def eval_statement(
        self,
        statement: grammar.Statement,
        states: list[Environment]
    ) -> list[Environment]:
        match statement:
            case grammar.If(_, condition, truthy_branch, falsey_branch):
                truthy_states, falsey_states = [], []
                for state in states:
                    if state[condition.identifier]:
                        truthy_states.append(state)
                    else:
                        falsey_states.append(state)
                return (
                    self.eval_statement(truthy_branch, truthy_states) +
                    self.eval_statement(falsey_branch, falsey_states)
                )

            case grammar.Emit(_, variables):
                #* EMIT adds the bindings of all given variables to the result
                #* set for each individual state.
                self.results.extend(
                    tuple(
                        state[variable.identifier]
                        for variable in variables
                    )
                    for state in states
                )
                return states

            case grammar.Block(_, statements):
                #* Blocks sequence the statements they contain such that each
                #* statement consumes the states produced by the statement
                #* preceeding it.
                for statement in statements[:-1]:
                    states = self.eval_statement(statement, states)
                return self.eval_statement(statements[-1], states)

            case grammar.Stop(_):
                #* STOP voids all current states and yield none instead.
                return []

            case grammar.NoOp(_):
                #* NOOP literally does nothing and just forwards the states.
                return states

            case grammar.Assignment(_, assigned_variables, expression):
                set_valued_inputs = {
                    argument.variable.identifier
                    for argument in expression.arguments
                    if argument.valuedness == grammar.Valuedness.SET
                }
                grouped_variables = [
                    variable.identifier
                    for variable in self.symbol_table
                    if variable.identifier not in set_valued_inputs
                ]
                assigned_variables = [
                    variable.identifier
                    for variable in assigned_variables
                ]

                next_states = []
                for fixed, grouped_states in groupby(
                    states,
                    key=lambda state: tuple(
                        state[variable]
                        for variable in grouped_variables
                    )
                ):
                    #! /!\ This DataFrame is created and bound here to allow
                    #!     DuckDB to find it as table through their
                    #!     replacement scans magic. ;)
                    __flummi_state__ = pd.DataFrame.from_records([
                        {
                            f"__{key}__": value
                            for key, value in state.items()
                        }
                        for state in grouped_states
                    ])

                    try:
                        formatted_sql = expression.source.format(
                            state='"__flummi_state__"',
                            **{
                                argument.variable.identifier:
                                f'"__{argument.variable.identifier}__"'
                                for argument in expression.arguments
                            }
                        )
                    except KeyError as e:
                        raise EvaluationError(
                            f"The query used variable {str(e)}, "
                            "but it was not supplied in the arguments to it.",
                            expression.location
                        ) from e

                    try:
                        duckdb.execute(formatted_sql)
                        results = duckdb.fetchall()
                    except Exception as e:
                        #? We wrap any errors DuckDB may produce in our own
                        #? exception type for prettier error messages.
                        raise EvaluationError(
                            str(e) +
                            f"\nCurrent scope:\n{__flummi_state__}",
                            expression.location
                        ) from e

                    #? We would like this to a static "pre-flight" check, but
                    #? without introspecting the user-provided SQL queries that
                    #? is not possible.
                    if (
                        expression.valuedness == grammar.Valuedness.SCALAR and
                        len(results) > 1
                    ):
                        raise EvaluationError(
                            "Expected expression to be scalar-valued "
                            "but it yielded a too many of results.\n"
                            f"Current scope:\n{__flummi_state__}",
                            expression.location
                        )
                    elif len(results) == 0:
                        raise EvaluationError(
                            "Expression produced no rows! "
                            "This behaviour is reserved for the STOP keyword.\n"
                            f"Current scope:\n{__flummi_state__}",
                            expression.location
                        )

                    next_states.extend(
                        (
                            #? variables that are "scalar-valued wrt. the
                            #? expression" retain old values
                            dict(zip(grouped_variables, fixed)) |

                            #? variables that are "set-valued wrt. the
                            #? expression" loose old values
                            dict.fromkeys(set_valued_inputs) |

                            #? variables that are assigned to gain new values
                            dict(zip(assigned_variables, bindings))
                        )
                        for bindings in results
                    )
                return next_states

        raise EvaluationError(
            f"Unsupported statement: {statement!s}",
            statement.location
        )
