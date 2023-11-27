import duckdb
import numpy
import io
import sys

from flummi.interpreter.interpreter import Interpreter
from flummi import parser

#print(interpreter.interpret.__doc__) 
#duckdb.sql("SELECT 42").show()

#sys.argv[1]

with io.open("examples/ray.fl", "r", encoding="utf-8") as file:
    data = file.read()

print(Interpreter().interpret(parser.parse(data)))
