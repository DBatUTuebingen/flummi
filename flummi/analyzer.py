from dataclasses import dataclass, field

from . import grammar, errors

__all__ = (
    "analyze",
    "SymbolTable",
)


class AnalyzerError(errors.FlummiError, name="Analyzer"):
    ...


type SymbolTable = dict[grammar.Variable, grammar.Type]
type VariableBindings = dict[grammar.Variable, grammar.Expression]


def analyze(
    program: grammar.Program
) -> tuple[grammar.Program, SymbolTable, tuple[grammar.Type, ...]]:
    return Analyzer().analyze_program(program)


@dataclass(slots=True)
class Analyzer:
    symbol_table: SymbolTable = field(init=False, default_factory=dict)
    emit_exists: bool = field(init=False, default=False)
    emit_width: int = field(init=False, default=0)
    is_scalar_valued: bool = field(init=False, default=False)
    initialised_variables: set[grammar.Variable] = field(init=False, default_factory=set)
    set_valued_variables: set[grammar.Variable] = field(init=False, default_factory=set)

    def analyze_program(
        self,
        program: grammar.Program
    ) -> tuple[grammar.Program, SymbolTable, tuple[grammar.Type, ...]]:
        if (
            len(program.function.parameters) == 0 and
            program.inputs is not None
        ):
            raise AnalyzerError(
                "Found input generating expression but didn't expect one.",
                program.inputs.location
            )

        program.function, emit_types = self.analyze_function(program.function)

        return program, self.symbol_table, emit_types

    def analyze_function(
        self,
        function: grammar.Function
    ) -> tuple[grammar.Function, tuple[grammar.Type, ...]]:
        self.symbol_table.update(function.parameters)
        self.initialised_variables.update(function.parameters)
        self.is_scalar_valued = function.valuedness == grammar.Valuedness.SCALAR
        self.emit_width = len(function.emits)
        function.body, _, stopped = self.analyze_statement(function.body)

        if not stopped:
            raise AnalyzerError(
                "Function ended without STOP intruction. "
                "Please explicitly mark your function exits.",
                function.body.location
            )

        if not self.emit_exists:
            raise AnalyzerError("Found no emits!", function.location)

        return function, function.emits

    def analyze_statement(
        self,
        statement: grammar.Statement,
    ) -> tuple[grammar.Statement, bool, bool]:
        match statement:
            case grammar.NoOp():
                #* NOOP statements do nothing, as such they can be elided
                #* without issue.
                return statement, True, False

            case grammar.Stop():
                #* STOP statements do exactly one thing and that is signaling
                #* that execution as stopped.
                return statement, False, True

            case grammar.Emit(location, to_emit):
                #? All emits need to emit the same number of variables as
                #? declared by the functions signature.
                if self.emit_width != len(to_emit):
                    raise AnalyzerError(
                        "Tried to emit different number of variables than "
                        f"declared by the function ({self.emit_width}).",
                        location
                    )

                for variable in to_emit:
                    self.analyze_variable(variable)

                #? If the function was not declared as set-valued ensure that
                #? the current emit is in a set-valued context.
                if self.is_scalar_valued:
                    if self.set_valued_variables:
                        raise AnalyzerError(
                            "Found EMIT in possibly set-valued context, "
                            "but the function is declared as scalar-valued.",
                            location
                        )

                    if self.emit_exists:
                        raise AnalyzerError(
                            "Found multiple EMITs along linear control path, "
                            "but the function is declared as scalar-valued.",
                            location
                        )

                self.emit_exists = True

                return statement, False, False

            case grammar.Declaration(location, variable, type):
                if variable in self.symbol_table:
                    raise AnalyzerError(
                        "Found re-declaration of variable "
                        f"{variable.identifier!r}.",
                        location
                    )

                self.symbol_table[variable] = type
                return statement, True, False

            case grammar.Assignment(_, variables, expression):
                self.analyze_expression(expression)
                self.initialised_variables.update(variables)

                for variable in variables:
                    self.analyze_variable(variable)

                if expression.valuedness is grammar.Valuedness.SET:
                    self.set_valued_variables.update(variables)

                return statement, False, False

            case grammar.Block(location, statements):
                new_statements, stopped = [], False
                for statement in statements:
                    statement, elide, stopped = self.analyze_statement(statement)
                    if not elide:
                        new_statements.append(statement)
                        if stopped:
                            break

                return (
                    grammar.Block(
                        location,
                        new_statements
                    ),
                    len(new_statements) == 0,
                    stopped
                )

            case grammar.If(location, condition, truthy, falsey):
                self.analyze_variable(condition)

                #? Cache value before the first branch. We need to reset this
                #? for the second branch.
                emit_exists = self.emit_exists
                truthy, elide_truthy, truthy_stopped = self.analyze_statement(truthy)
                truthy_contains_emit = self.emit_exists

                #? Reapply cached value for second branch.
                self.emit_exists = emit_exists

                falsey, elide_falsey, falsey_stopped = self.analyze_statement(falsey)
                self.emit_exists |= truthy_contains_emit

                return (
                    grammar.If(
                        location,
                        condition,
                        grammar.NoOp(truthy.location) if elide_truthy else truthy,
                        grammar.NoOp(falsey.location) if elide_falsey else falsey,
                    ),
                    elide_truthy and elide_falsey,
                    truthy_stopped and falsey_stopped
                )

        raise AnalyzerError(
            "Found unknown statement.",
            statement.location
        )

    def analyze_expression(self, expression: grammar.Expression):
        for argument in expression.arguments:
            self.analyze_argument(argument)

    def analyze_argument(self, argument: grammar.Argument):
        self.analyze_variable(argument.variable)
        if argument.valuedness is grammar.Valuedness.SET:
            self.set_valued_variables.discard(argument.variable)

    def analyze_variable(self, variable: grammar.Variable):
        if variable not in self.symbol_table:
            raise AnalyzerError(
                f"Tried to use undeclared variable {variable.identifier!r}.",
                variable.location
            )

        if variable not in self.initialised_variables:
            raise AnalyzerError(
                f"Tried to use uninitialised variable {variable.identifier!r}.",
                variable.location
            )
