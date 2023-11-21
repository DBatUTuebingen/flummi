from typing import TypeVar

from ..grammars import proc, common
from .. import parser

E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)

__all__ = (
    "interpret"
)

#TODO: add documentation
def interpret(program: proc.Program[E, T]):

    #get return type and first statement of function from program
    return_type, first_function_statement = program_helper(program)

    #start going down the statements
    match first_function_statement:
        case _:
            print("nothing to see here yet")

    #TODO: check return type
    ...

def program_helper(program: proc.Program[E,T])-> tuple(proc.Statement[E,T],common.Type[T]):
    # for faster access
    f = program.function
    
    #TODO: Error for mismatched arguments
    if len(f.parameters) != len(program.inputs):  
        ...

    #create assignments for parameters <- arguments
    #add them to a block
    #add the block at the beginning of the function body
    temp_block = proc.Block([]) 

    for x in range(0, len(f.parameters)):
        temp_assignment = proc.Assignment(f.parameters.keys[x],program.inputs[x])
        temp_block.statements.append(temp_assignment)

    temp_block.statements.append(f.body)
    f.body = temp_block

    return f.body, f.emits