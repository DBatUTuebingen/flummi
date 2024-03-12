from . import grammar, errors

__all__ = (
  "analyze",
  "SymbolTable",
)


class AnalyzerError(errors.FlummiError, name="Analyzer"):
  ...


type SymbolTable = dict[grammar.Variable, grammar.Type]
type VariableBindings = dict[grammar.Variable, grammar.Expression]


def analyze(program: grammar.Program) -> tuple[grammar.Program, SymbolTable, tuple[grammar.Type, ...]]:
  return Analyzer().analyze(program)


class Analyzer:
  def __init__(self) -> None:
    self._symbol_table: SymbolTable = {}
    self._emit_exists: bool = False
    self._emit_width: int = 0
    self._is_scalar_valued: bool = False
    self._initialised_variables: set[grammar.Variable] = set()
    self._set_valued_variables: set[grammar.Variable] = set()

  def analyze(self, program: grammar.Program) -> tuple[grammar.Program, SymbolTable, tuple[grammar.Type, ...]]:
    if len(program.function.parameters) == 0 and program.inputs is not None:
      raise AnalyzerError("Found input generating expression but didn't expect one.", program.inputs.location)

    program.function, emit_types = self._analyze_function(program.function)

    return program, self._symbol_table, emit_types

  def _analyze_function(self, function: grammar.Function) -> tuple[grammar.Function, tuple[grammar.Type, ...]]:
    self._symbol_table.update(function.parameters)
    self._initialised_variables.update(function.parameters)
    self._is_scalar_valued = function.valuedness is grammar.Valuedness.SCALAR
    self._emit_width = len(function.emits)
    function.body, _ = self._analyze_statement(function.body)

    if not self._emit_exists:
      raise AnalyzerError("Found no emits!", function.location)

    return function, function.emits

  def _analyze_statement(self, statement: grammar.Statement) -> tuple[grammar.Statement, bool]:
    match statement:
      case grammar.NoOp():
        return statement, True

      case grammar.Stop():
        return statement, False

      case grammar.Emit(location, to_emit):
        if self._emit_width != len(to_emit):
          raise AnalyzerError(
            f"Tried to emit different number of variables than declared by the function ({self._emit_width}).",
            location
          )
        for variable in to_emit:
          self._analyze_variable(variable)
        if self._is_scalar_valued and (self._emit_exists or self._set_valued_variables):
          raise AnalyzerError(
            "Found function to be set-valued but it was declared as scalar valued.",
            location
          )
        self._emit_exists = True
        return statement, False

      case grammar.Declaration(location, variable, type):
        if variable in self._symbol_table:
          raise AnalyzerError(f"Found re-declaration of {variable}!", location)
        self._symbol_table[variable] = type
        return statement, True

      case grammar.Assignment(_, variables, expression):
        self._analyze_expression(expression)
        self._initialised_variables.update(variables)
        for variable in variables:
          self._analyze_variable(variable)
        if expression.valuedness is grammar.Valuedness.SET:
          self._set_valued_variables.update(variables)
        return statement, False

      case grammar.Block(location, statements):
        new_statements = []
        for sub_statement in statements:
          sub_statement, elide = self._analyze_statement(sub_statement)
          if not elide:
            new_statements.append(sub_statement)
        return grammar.Block(location, new_statements), len(new_statements) == 0

      case grammar.If(location, condition, truthy, falsey):
        self._analyze_variable(condition)
        truthy, elide_truthy = self._analyze_statement(truthy)
        falsey, elide_falsey = self._analyze_statement(falsey)
        return grammar.If(
          location,
          condition,
          grammar.NoOp(truthy.location) if elide_truthy else truthy,
          grammar.NoOp(falsey.location) if elide_falsey else falsey,
        ), elide_truthy and elide_falsey

    raise AnalyzerError(
      f"Found unknown statement: {statement}",
      statement.location
    )

  def _analyze_expression(self, expression: grammar.Expression):
    for argument in expression.arguments:
      self._analyze_argument(argument)

  def _analyze_argument(self, argument: grammar.Argument):
    self._analyze_variable(argument.variable)
    if argument.valuedness is grammar.Valuedness.SET:
      self._set_valued_variables.discard(argument.variable)

  def _analyze_variable(self, variable: grammar.Variable):
    if variable not in self._symbol_table:
      raise AnalyzerError(
        f"Tried to use undeclared variable {variable}",
        variable.location
      )

    if variable not in self._initialised_variables:
      raise AnalyzerError(
        f"Tried to use uninitialised variable {variable}",
        variable.location
      )
