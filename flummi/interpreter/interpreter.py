import duckdb

from typing import TypeVar

from ..grammars import proc, common
from .. import parser

E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)

__all__ = (
    "interpret"
)

def interpret(program: proc.Program[E, T]) -> list[duckdb.DuckDBPyRelation]:
    """
    Interprets given program

    Parameters:

    Returns:

    """

    #get return type and first statement of function from program
    first_function_statement = program_helper(program)

    #go through statements
    enviornment = statement_helper(first_function_statement, env= dict{}, result_list= [])

    #TODO: get list of results
    ...

def program_helper(program: proc.Program[E,T])-> proc.Statement[E,T]:
    """
    Assigns program arguments to function parameters and appends them at the front of the statement list of the function

    Parameters:
    program (proc.Program[E, T]): program to be interpreted

    Returns:
    proc.Statement[E,T]: first statement of function
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
        temp_assignment = proc.Assignment(f.parameters.keys[x],program.inputs[x])
        temp_block.statements.append(temp_assignment)

    temp_block.statements.append(f.body)
    f.body = temp_block

    return f.body

def statement_helper(statement: proc.Statement[E, T], env: dict[common.Variable, common.Expression[E]], result_list: list[duckdb.DuckDBPyRelation]) -> dict[common.Variable, common.Expression[E]]:
    """
    Goes through all statements of a function to return result(s)

    Parameters:

    Returns:
    
    """

    match statement:
        case proc.Loop(name, body):
            ...
        case proc.Continue(name):
            ...
        case proc.Break(name):
            ...
        case proc.If(condition, t_branch, f_branch):
            ...
        case proc.Emit(to_emit):

            result = duckdb.sql()
            result_list.append()
            return env

        case proc.Declaration(variable, type):
            # do i need this?
            return env

        case proc.Assignment(variable, expression):
            env[variable] = duckdb.sql("SELECT " + expression)
            return env

        case proc.Block(statements):
            #saved_environment = env
            for block_statement in statements:
                env = statement_helper(block_statement, env, result_list)
            
        case proc.Stop():
            return env

        case _:
            print("nothing to see here yet")