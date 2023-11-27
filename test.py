import duckdb
import numpy
import io

from flummi.interpreter import interpreter
from flummi import parser

#print(interpreter.interpret.__doc__) 
#duckdb.sql("SELECT 42").show()

with io.open("examples/mul.fl", "r", encoding="utf-8") as file:
    data = file.read()

print(interpreter.Interpreter.interpret(parser.parse(data)))
