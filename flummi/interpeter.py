from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass, field, InitVar
from typing import Any

import duckdb

from . import grammar, errors, sql
from .utils import _indent


__all__ = (
    "interpret",
)


class EvaluationError(errors.FlummiError, name="evaluation"):
    ...


QUERY_CACHE: dict[grammar.Location, str] = {}


@dataclass
class Thread:
    start: InitVar[grammar.Statement]
    environment: dict[str, Any]       = field(            default_factory=dict)
    stack: list[grammar.Statement]    = field(init=False, default_factory=list)
    threads: dict[str, Thread]        = field(init=False, default_factory=dict)
    results: list[tuple[Any, ...]]    = field(init=False, default_factory=list)
    done   : bool                     = field(init=False, default=False)

    def __post_init__(self, start: grammar.Statement):
        self.stack.append(start)

    def step(
        self,
        program: grammar.Program,
        symbol_table: dict[grammar.Variable, grammar.Type]
    ):
        if self.done:
            raise EvaluationError("Tried to step thread after stop!")

        statement = self.stack.pop()

        match statement:
            case grammar.NoOp():
                ...

            case grammar.Block(_, statements):
                self.stack.extend(statements[::-1])

            case grammar.Stop():
                self.done = True

            case grammar.Emit(_, variables):
                self.results.append(tuple(
                    self.environment[variable.identifier]
                    for variable in variables
                ))

            case grammar.If(_, condition, t_branch, f_branch):
                match condition:
                    case grammar.VariableCheck(_, variable):
                        choice = self.environment[variable.identifier]
                        if not isinstance(choice, bool):
                            raise EvaluationError(
                                "Variable condition is non-boolean.",
                                condition.location,
                                "",
                                "Current scope:",
                                *(
                                    f"{variable} := {value!r}"
                                    for variable, value in self.environment.items()
                                ),
                            )
                    case grammar.HandleCheck(_, handle):
                        choice = self.threads[handle.identifier].done
                self.stack.append(t_branch if choice else f_branch)

            case grammar.Loop(_, name, body):
                self.stack.append(statement)
                self.stack.append(body)

            case grammar.Continue(location, name) | grammar.Break(location, name):
                while self.stack:
                    next = self.stack.pop()
                    match next:
                        case grammar.Loop(_, _name, body) if name == _name:
                            if isinstance(statement, grammar.Continue):
                                self.stack.append(next)
                            break
                else:
                    ...

            case grammar.Assignment(location, variables, expression):
                if location not in QUERY_CACHE:
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
                                for variable, value in self.environment.items()
                            ),
                            "",
                            "Error:",
                            repr(e)
                        ) from e
                    QUERY_CACHE[location] = query
                else:
                    query = QUERY_CACHE[location]
                parameters = [
                    self.environment[free_variable.identifier]
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
                            for variable, value in self.environment.items()
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
                            for variable, value in self.environment.items()
                        ),
                    )

                self.environment.update(
                    (variable.identifier, value)
                    for variable, value in zip(variables, row)
                )

            case grammar.Spawn(_, handle, target, arguments):
                function = program.functions[target]
                self.threads[handle.identifier] = Thread(
                    start=function.body,
                    environment={
                        parameter.identifier:
                        self.environment[argument.identifier]
                        for parameter, argument in zip(
                            function.parameters,
                            arguments
                        )
                    }
                )

            case grammar.Join(_, handle):
                thread = self.threads[handle.identifier]
                while not thread.done:
                    thread.step(program, symbol_table)

            case grammar.Fetch(location, handle, variables):
                thread = self.threads[handle.identifier]
                if thread.done and not thread.results:
                    raise EvaluationError(
                        "Tried to fetch past the end of a thread.",
                        location
                    )

                while not thread.results:
                    thread.step(program, symbol_table)

                row = thread.results.pop(0)

                self.environment.update(
                    (variable.identifier, value)
                    for variable, value in zip(variables, row)
                )

            case _:
                raise EvaluationError(
                    "Encountered unsupported statement.",
                    statement.location
                )

def interpret(
    program: grammar.Program,
    symbol_table: dict[grammar.Variable, grammar.Type]
) -> Iterator[tuple[Any, ...]]:

    function = program.main_function

    if program.inputs is not None:
        initial_statement = grammar.Block(
            program.location,
            [
                grammar.Assignment(
                    program.inputs.location,
                    list(function.parameters.keys()),
                    program.inputs
                ),
                function.body
            ]
        )
    else:
        initial_statement = function.body

    main_thread = Thread(initial_statement)

    while not main_thread.done:
        main_thread.step(program, symbol_table)

    yield from main_thread.results

