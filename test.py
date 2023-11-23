import duckdb
from flummi.interpreter import interpreter

print(interpreter.interpret.__doc__) 
duckdb.sql("SELECT 42").show()
