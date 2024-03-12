from flummi.interpreter.interpreter import Interpreter
from time import time
from flummi.parser import parse
import duckdb

width = 2
height = 2
source = ""

with open('./examples/ray_setup.sql', 'r', encoding="utf8") as file:
    filecontent = file.read()
    duckdb.execute(filecontent, {"width": width, "height": height})

with open('./examples/ray.fl', 'r', encoding="utf8") as file:
    source = file.read()

start = time()

ast = parse(source)

for index in range(1, 1 + width * height):
    ast.inputs[0].source = str(index)
    Interpreter.return_list = []
    Interpreter.env = {}
    Interpreter.types = {}
    results = Interpreter().interpret(ast)
    print("RESULTS: " + str(results))
    

stop = time()

print(f"Time taken: {stop - start}s")