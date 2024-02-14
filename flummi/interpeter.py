from collections.abc import Iterator
from dataclasses import dataclass, field
from itertools import chain
from typing import Any

import duckdb

from . import grammar

__all__ = (
    "interpret",
)


def interpret(program: grammar.Program, symbol_table: dict[grammar.Variable, grammar.Type]) -> Iterator[Any]:
    yield from Interpreter(symbol_table).eval_program(program)


# used to move up the call stack for BREAK, CONTINUE and STOP
class LoopBreak(Exception): ...
class LoopContinue(Exception): ...
class Stop(Exception): ...


@dataclass
class Interpreter:
    symbol_table: dict[grammar.Variable, grammar.Type]
    environment: dict[grammar.Variable, duckdb.DuckDBPyRelation] = field(init=False, default_factory=dict)

    def eval_program(self, program: grammar.Program)-> Iterator[Any]:
        """
        Assigns program arguments to function parameters and appends them at the front of the statement list of the function

        Parameters: program (grammar.Program): program to be interpreted

        Returns: None
        """
        try:
            yield from self.eval_statement(grammar.Block([
                *chain.from_iterable(
                    (
                        grammar.Declaration(parameter, type),
                        grammar.Assignment(parameter, expression),
                    )
                    for (parameter, type), expression in zip(
                        program.function.parameters.items(),
                        program.inputs
                    )
                ),
                program.function.body
            ]))
        except Stop:
            ...

    def eval_statement(self, statement: grammar.Statement) -> Iterator[Any]:
        """
        Goes through all statements of a function to return result(s)

        Parameters: statement (grammar.Statement): statement to be matched

        Returns: None

        """
        match statement:
            case grammar.Loop(name, body):
                while(True):
                    try:
                        yield from self.eval_statement(body)
                    except LoopBreak as e:
                        if name == e.args[0]:
                            break
                        else:
                            raise e
                    except LoopContinue as e:
                        if name == e.args[0]:
                            continue
                        else:
                            raise e

            case grammar.Continue(name):
                raise LoopContinue(name)

            case grammar.Break(name):
                raise LoopBreak(name)

            case grammar.If(condition, t_branch, f_branch):
                yield from self.eval_statement(t_branch if self.eval_expression(condition) else f_branch)

            case grammar.Emit(to_emit):
                yield self.eval_expression(to_emit)

            case grammar.Assignment(variable, expression):
                self.environment[variable] = self.eval_expression(expression)

            case grammar.Block(statements):
                for block_statement in statements:
                    yield from self.eval_statement(block_statement)

            case grammar.Stop():
                raise Stop()

            case _:
                ...

    def eval_expression(self, expression: grammar.Expression) -> Any:
        """
        Inserts values into placeholders, runs it as a DuckDB query and returns the result

        Parameters: expression (grammar.Expression): expression to be queried

        Returns: str: Value of the expression in as a str

        """
        result = duckdb.execute(
            "SELECT " + expression.source.format(*(
                f"(${i+1} :: {self.symbol_table[free_variable].source})"
                for i, free_variable in enumerate(expression.free_variables)
            )),
            [
                self.environment[free_variable]
                for free_variable in expression.free_variables
            ]
        )

        if (row := result.fetchone()) is not None:
            return row[0]
        else:
            raise RuntimeError("Embedded SQL expression produced no rows.")
