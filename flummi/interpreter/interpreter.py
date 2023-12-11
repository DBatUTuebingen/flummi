import duckdb
import re

from typing import TypeVar

from ..grammars import proc, common

E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)

__all__ = (
    "Interpreter",
)


#used to move up the call stack for BREAK, CONTINUE and STOP
class LoopBreak(Exception): ...
class LoopContinue(Exception): ...
class Stop(Exception): ...

class Interpreter():
   
    return_list: list[duckdb.DuckDBPyRelation] = []
    env: dict[common.Variable, any] = {}
    types: dict[common.Variable, any] = {}

    def interpret(self, program: proc.Program[E, T]) -> list[duckdb.DuckDBPyRelation]:
        """
        Interprets given program

        Parameters: program (proc.Program[E, T]): program to be interpreted

        Returns: None

        """

        first_function_statement = self.program_helper(program)

        try: 
            self.statement_helper(first_function_statement)
        except Stop:
            return self.return_list

        return self.return_list

    def program_helper(self, program: proc.Program[E,T])-> None:
        """
        Assigns program arguments to function parameters and appends them at the front of the statement list of the function

        Parameters: program (proc.Program[E, T]): program to be interpreted

        Returns: None
        """

        f = program.function
        
        if len(f.parameters) != len(program.inputs):  
            raise TypeError("Incorrect number of arguments given.")

        temp_block = proc.Block([]) 
        parameter_keys = list(f.parameters.keys())
        parameter_values = list(f.parameters.values())

        for x in range(0, len(f.parameters)):
            temp_declaration = proc.Declaration(parameter_keys[x], parameter_values[x])
            temp_assignment = proc.Assignment(parameter_keys[x],program.inputs[x]) 
            temp_block.statements.append(temp_declaration)
            temp_block.statements.append(temp_assignment)

        temp_block.statements.append(f.body)
        
        f.body = temp_block

        return f.body

    def statement_helper(self, statement: proc.Statement[E, T]) -> None:
        """
        Goes through all statements of a function to return result(s)

        Parameters: statement (proc.Statement[E, T]): statement to be matched

        Returns: None
        
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
                    except LoopContinue as e:
                        if name == e.args[0]:
                            continue
                        else:
                            raise e
            
            case proc.Continue(name):
                raise LoopContinue(name)
            
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

            case proc.Declaration(variable, type):
                self.types[variable] = re.match(r"(\w+)",type.source).group(0)

            case proc.Assignment(variable, expression):
                if variable not in self.types:
                    raise NameError("Variable " + variable.identifier + " has not been declared yet.")
                self.env[variable] = self.expression_helper(expression)

            case proc.Block(statements):
                for block_statement in statements:
                    self.statement_helper(block_statement)

            case proc.Stop():
                raise Stop
                
            

    def expression_helper(self, expression: common.Expression[E]) -> str:
        """
        Inserts values into placeholders, runs it as a DuckDB query and returns the result

        Parameters: expression (common.Expression[E]): expression to be queried

        Returns: str: Value of the expression in as a str
        
        """

        # makes a list with all unique placeholer numbers in the expression
        placeholder_list = list(dict.fromkeys(re.findall(r"\{(\d)\}", expression.source)))

        # if free veriables exist in the expression 
        if len(expression.free_variables) != 0:
            # then get its type and its corresponding placement number 
            placeholder_tuple = [(self.types[expression.free_variables[int(x)]], placeholder_list[int(x)]) for x in placeholder_list]
            # and make a new String where each placeholder number is incremented by one (for sql) and bring it in the form of ({x} :: type)
            placeholder_list = list(map(lambda tuple: f"({{{str(int(tuple[1])+1)}}} :: {tuple[0]})", placeholder_tuple))

        # use these new strings and format the expression
        temp_expression = expression.source.format(*placeholder_list)
        # substitute all python placeholders with sql placeholders
        temp_expression = re.sub(r"\{(\d)\}", r"$\1", temp_expression)
        
        #run the sql query and return it
        return duckdb.execute(f"SELECT ({temp_expression})", [self.env[x] for x in expression.free_variables]).fetchone()[0]


