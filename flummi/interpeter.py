from collections.abc import Iterator
from dataclasses import dataclass, field
import duckdb
import re

from typing import Any

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

        f = program.function

        temp_block = grammar.Block([])
        parameter_keys = list(f.parameters.keys())
        parameter_values = list(f.parameters.values())

        for x in range(0, len(f.parameters)):
            temp_declaration = grammar.Declaration(parameter_keys[x], parameter_values[x])
            temp_assignment = grammar.Assignment(parameter_keys[x],program.inputs[x])
            temp_block.statements.append(temp_declaration)
            temp_block.statements.append(temp_assignment)

        temp_block.statements.append(f.body)

        try:
            yield from self.eval_statement(temp_block)
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

        # makes a list with all unique placeholder numbers in the expression
        placeholder_list = list(dict.fromkeys(re.findall(r"\{(\d)\}", expression.source)))

        # if free variables exist in the expression
        if len(expression.free_variables) != 0:
            # then get its type and its corresponding placement number
            placeholder_tuple = [(self.symbol_table[expression.free_variables[int(x)]].source, placeholder_list[int(x)]) for x in placeholder_list]
            # and make a new String where each placeholder number is incremented by one (for sql) and bring it in the form of ({x} :: type)
            placeholder_list = list(map(lambda tuple: f"({{{str(int(tuple[1])+1)}}} :: {tuple[0]})", placeholder_tuple))

        # use these new strings and format the expression
        temp_expression = expression.source.format(*placeholder_list)
        # substitute all python placeholders with sql placeholders
        temp_expression = re.sub(r"\{(\d)\}", r"$\1", temp_expression)

        #run the sql query and return it
        if (row := duckdb.execute(f'SELECT ({temp_expression}) AS "%result%"', [self.environment[x] for x in expression.free_variables]).fetchone()) is not None:
            return row[0]
        else:
            raise RuntimeError("Embedded SQL expression produced no rows.")
