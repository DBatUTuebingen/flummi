import duckdb
import numpy
import re

from typing import TypeVar

from ..grammars import proc, common
from .. import parser

E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)

__all__ = (
    "interpret",
)


class LoopBreak(Exception): ...

class Interpreter():
    return_list: list[duckdb.DuckDBPyRelation] = []
    env: dict[common.Variable, any] = {}
    types: dict[common.Variable, any] = {}

    def interpret(self, program: proc.Program[E, T]) -> list[duckdb.DuckDBPyRelation]:
        """
        Interprets given program

        Parameters:

        Returns:

        """

        #get return type and first statement of function from program
        first_function_statement = self.program_helper(program)

        #go through statements
        self.statement_helper(first_function_statement)

        return self.return_list

    def program_helper(self, program: proc.Program[E,T])-> None:
        """
        Assigns program arguments to function parameters and appends them at the front of the statement list of the function

        Parameters:

        Returns:
        """

        # for faster access
        f = program.function
        
        if len(f.parameters) != len(program.inputs):  
            raise TypeError("Incorrect number of arguments given.")

        #create assignments for parameters <- arguments
        #add them to a block
        #add the block at the beginning of the function body
        temp_block = proc.Block([]) 

        for x in range(0, len(f.parameters)):
            parameter_keys = list(f.parameters.keys())
            parameter_values = list(f.parameters.values())
            temp_assignment = proc.Assignment(parameter_keys[x],program.inputs[x])
            temp_declaration = proc.Declaration(parameter_keys[x], parameter_values[x])
            temp_block.statements.append(temp_declaration)
            temp_block.statements.append(temp_assignment)
        
        temp_block.statements.append(f.body)
        f.body = temp_block

        return f.body

    def statement_helper(self, statement: proc.Statement[E, T]) -> dict[common.Variable, any]:
        """
        Goes through all statements of a function to return result(s)

        Parameters:

        Returns:
        
        """
        match statement:
            case proc.Loop(name, body):
                while(True):
                    try:
                        self.statement_helper(body)
                    except LoopBreak as e:
                        if name == e.args[0]:
                            break
                        else:
                            raise e
                ...
            
            case proc.Continue(name):
                ...
            
            case proc.Break(name):
                raise LoopBreak(name)
            
            case proc.If(condition, t_branch, f_branch):
                if self.env[condition]:
                    self.statement_helper(t_branch)
                else:
                    self.statement_helper(f_branch)

            case proc.Emit(to_emit):
                result = self.expression_helper(to_emit)
                self.return_list.append(result)
                ...

            case proc.Declaration(variable, type):
                self.types[variable] = re.match(r"(\w+)",type.source).group(0)

            case proc.Assignment(variable, expression):
                self.env[variable] = self.expression_helper(expression)

            case proc.Block(statements):
                for block_statement in statements:
                    self.statement_helper(block_statement)
                
            case proc.Stop():
                ...
            

    def expression_helper(self, expression: common.Expression[E]) -> str:
        placeholder_list = list(dict.fromkeys(re.findall(r"\{(\d)\}", expression.source)))

        if len(expression.free_variables) != 0:
            placeholder_tuple = [(self.types[expression.free_variables[int(x)]], placeholder_list[int(x)]) for x in placeholder_list]
            placeholder_list = list(map(lambda tuple: f"({{{str(int(tuple[1])+1)}}} :: {tuple[0]})", placeholder_tuple))

        temp_expression = expression.source.format(*placeholder_list)
        temp_expression = re.sub(r"\{(\d)\}", r"$\1", temp_expression)
        
        return duckdb.execute(f"SELECT ({temp_expression})", [self.env[x] for x in expression.free_variables]).fetchone()[0]

