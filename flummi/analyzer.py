from warnings import warn

from . import grammar

__all__ = (
  "analyze",
  "SymbolTable",
)


type SymbolTable = dict[grammar.Variable, grammar.Type]
type VariableBindings = dict[grammar.Variable, grammar.Expression]


def analyze(program: grammar.Program) -> tuple[grammar.Program, SymbolTable, grammar.Type, VariableBindings]:
  return Analyzer().analyze(program)


class Analyzer:
  def __init__(self) -> None:
    self._symbol_table: SymbolTable = {}
    self._used_symbols: set[grammar.Variable] = set()
    self._number_of_inputs: int = 0
    self._loop_names: set[str] = set()
    self._loop_scope: list[str] = []
    self._emit_exists: bool = False

  def analyze(self, program: grammar.Program) -> tuple[grammar.Program, SymbolTable, grammar.Type, VariableBindings]:
    self._number_of_inputs = len(program.inputs)
    for input in program.inputs:
      if len(input.free_variables) > 0:
        raise ValueError("Input expression can't have free variables!")

    program.function, emit_type = self._analyze_function(program.function)

    variable_bindings = dict(zip(program.function.parameters.keys(),program.inputs))

    return program, self._symbol_table, emit_type, variable_bindings

  def _analyze_function(self, function: grammar.Function) -> tuple[grammar.Function, grammar.Type]:
    if len(function.parameters) != self._number_of_inputs:
      raise ValueError("Number of inputs and function parameters do not match!")
    self._symbol_table.update(function.parameters)

    function.body, elide = self._analyze_statement(function.body)

    if elide:
      warn("Found top expression to be elidable!", source="Analysis")
      function.body = grammar.NoOp()

    if not self._emit_exists:
      raise ValueError("Found no emits!")

    if not self._used_symbols.issubset(self._symbol_table):
      raise ValueError(f"Found use of undeclared variables!")

    return function, function.emits

  def _analyze_statement(self, statement: grammar.Statement) -> tuple[grammar.Statement, bool]:
    match statement:
      case grammar.NoOp():
        return statement, True

      case grammar.Stop():
        return statement, False

      case grammar.Emit(expression):
        self._emit_exists = True
        self._analyze_expression(expression)
        return statement, False

      case grammar.Declaration(variable, type):
        if variable in self._symbol_table:
          raise ValueError(f"Found re-declaration of {variable}!")
        self._symbol_table[variable] = type
        return statement, True

      case grammar.Assignment(variable, expression):
        self._analyze_variable(variable)
        self._analyze_expression(expression)
        return statement, False

      case grammar.Block(statements):
        new_statements = []
        for sub_statement in statements:
          sub_statement, elide = self._analyze_statement(sub_statement)
          if not elide:
            new_statements.append(sub_statement)
        return grammar.Block(new_statements), len(new_statements) == 0

      case grammar.If(expression, truthy, falsey):
        self._analyze_expression(expression)
        truthy, elide_truthy = self._analyze_statement(truthy)
        falsey, elide_falsey = self._analyze_statement(falsey)
        return grammar.If(
          expression,
          grammar.NoOp() if elide_truthy else truthy,
          grammar.NoOp() if elide_falsey else falsey,
        ), elide_truthy and elide_falsey

      case grammar.Loop(name, body):
        if name in self._loop_names:
          raise ValueError(f"Found reused loop name {name}")
        self._loop_names.add(name)
        self._loop_scope.append(name)
        body, elide = self._analyze_statement(body)
        del self._loop_scope[-1]
        return grammar.Loop(name, body), elide

      case grammar.Continue(name):
        if name not in self._loop_names:
          raise ValueError(f"Tried to continue unknown loop {name}")
        if name not in self._loop_scope:
          raise ValueError(f"Tried to continue out-of-scope loop {name}")
        return statement, False

      case grammar.Break(name):
        if name not in self._loop_names:
          raise ValueError(f"Tried to break unknown loop {name}")
        if name not in self._loop_scope:
          raise ValueError(f"Tried to break out-of-scope loop {name}")
        return statement, False

      case _:
        raise ValueError(f"Found unknown statement: {statement}")

  def _analyze_expression(self, expression: grammar.Expression):
    for free_variable in expression.free_variables:
      self._analyze_variable(free_variable)

  def _analyze_variable(self, variable: grammar.Variable):
      if variable not in self._symbol_table:
        warn(f"Use of possibly undeclared variable {variable}", source="Analysis")
      self._used_symbols.add(variable)
