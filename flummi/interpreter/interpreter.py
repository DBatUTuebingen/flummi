import duckdb
import numpy

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

    def interpret(program: proc.Program[E, T]) -> list[duckdb.DuckDBPyRelation]:
        """
        Interprets given program

        Parameters:

        Returns:

        """

        #get return type and first statement of function from program
        first_function_statement = Interpreter.program_helper(program)

        #go through statements
        _ = Interpreter.statement_helper(first_function_statement)

        return Interpreter.return_list

    def program_helper(program: proc.Program[E,T])-> proc.Statement[E,T]:
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
            parameter_list = list(f.parameters.keys())
            temp_assignment = proc.Assignment(parameter_list[x],program.inputs[x])
            temp_block.statements.append(temp_assignment)

        temp_block.statements.append(f.body)
        f.body = temp_block

        return f.body

    def statement_helper(statement: proc.Statement[E, T]) -> dict[common.Variable, any]:
        """
        Goes through all statements of a function to return result(s)

        Parameters:

        Returns:
        
        """
        env = Interpreter.env

        match statement:
            case proc.Loop(name, body):
                while(True):
                    try:
                        env = Interpreter.statement_helper(body)
                    except LoopBreak as e:
                        if name == e.args[0]:
                            break
                        else:
                            raise e
                return env
            
            case proc.Continue(name):
                return env
            
            case proc.Break(name):
                raise LoopBreak(name)
            
            case proc.If(condition, t_branch, f_branch):
                condition_str = Interpreter.replace_values(condition, env[condition], env)
                condition_result = duckdb.execute("SELECT " + condition_str).fetchone()[0]
                if condition_result:
                    return Interpreter.statement_helper(t_branch)
                else:
                    return Interpreter.statement_helper(f_branch)

            case proc.Emit(to_emit):
                values = []
                for variable in to_emit.free_variables:
                    value = Interpreter.replace_values(variable, env[variable], env)
                    values.append(value)
                
                formatted_emit = to_emit.source.format(*values)
                result = duckdb.sql("SELECT " + formatted_emit)
                Interpreter.return_list.append(result)
                return env

            case proc.Declaration(variable, type):
                return env

            case proc.Assignment(variable, expression):
                if variable in env.keys():
                    env[variable] = common.Expression(Interpreter.replace_values(variable, expression, env),[])
                else: 
                    env[variable] = expression
                return env

            case proc.Block(statements):
                for block_statement in statements:
                    env = Interpreter.statement_helper(block_statement)
                return env
                
            case proc.Stop():
                return env
            

    def replace_values(variable: common.Variable, expression: common.Expression[E], env: dict[common.Variable, any]) -> str:
        formatted_exp = f"{expression.source}".format(*expression.free_variables)
        
        if(expression.free_variables == 0):    
            value = [*duckdb.execute("SELECT " + formatted_exp).fetchnumpy().values()][0][0]
            return value
        
        formatted_exp = f"{expression.source}".format(*list(map(lambda x: Interpreter.replace_values(x, env[x], env), expression.free_variables)))
        
        return formatted_exp
