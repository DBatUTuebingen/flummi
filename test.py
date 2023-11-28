import duckdb
import numpy
import io
import sys

from flummi.interpreter.interpreter import Interpreter
from flummi import parser

with io.open(sys.argv[1], "r") as file:
    duckdb.execute(file.read())
             
with io.open("examples/ray.fl", "r", encoding="utf-8") as file:
    data = file.read()

print(Interpreter().interpret(parser.parse(data)))
