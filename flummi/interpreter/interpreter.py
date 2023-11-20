from typing import TypeVar

from ..grammars import proc, common
from .. import parser

E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)

__all__ = (
    "interpret"
)

#TO DO: add documentation
def interpret(program: proc.Program[E, T]):

    #process inputs in DuckDB and get function
    processed_inputs, program_function = program_helper(program)

    #get return type and the beginning statement of the function
    return_type, statement = function_helper(processed_inputs, program_function)

    #start going down the statements
    match statement:
        case _:
            print("nothing to see here yet")

    #TO DO: check return type
    ...

def program_helper(program: proc.Program[E,T])-> tuple(list[common.Expression[E]],proc.Function[E,T]):
    #TO DO: need to integrate DuckDB
    processed_inputs: list[common.Expression[E]] = program.inputs
    program_function: proc.Function = program.function
    return processed_inputs, program_function

def function_helper(inputs: list[common.Expression[E]], f: proc.Function[E,T]) -> tuple(T, proc.Statement[E, T]):
    ...
    #TO DO: assign input values to function variables, can probably just use Assignment structure and add them to the top of the Block list