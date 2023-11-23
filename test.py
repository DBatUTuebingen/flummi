import duckdb
import numpy

from flummi.interpreter import interpreter
from flummi import parser

#print(interpreter.interpret.__doc__) 
#duckdb.sql("SELECT 42").show()

with open("examples/test.fl") as file:
    data = file.read()

print(interpreter.interpret(parser.parse(data)))
