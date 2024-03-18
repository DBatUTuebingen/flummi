from dataclasses import dataclass, field, replace

from . import grammar, errors

__all__ = (
    "analyze",
    "SymbolTable",
)


class AnalysisError(errors.FlummiError, name="analysis"):
    ...


type SymbolTable = dict[grammar.Variable, grammar.Type]


def analyze(
    program: grammar.Program
) -> tuple[grammar.Program, SymbolTable]:
    return Analyzer().analyze(program)


@dataclass
class Analyzer:
    symbol_table     : SymbolTable                  = field(init=False, default_factory=dict)
    bound_symbols    : set[grammar.Variable]        = field(init=False, default_factory=set)
    number_of_inputs : int                          = field(init=False, default=0)
    loop_names       : set[grammar.Variable]        = field(init=False, default_factory=set)
    loop_scope       : list[grammar.Variable]       = field(init=False, default_factory=list)
    loop_broken      : dict[grammar.Variable, bool] = field(init=False, default_factory=dict)
    loop_stopped     : dict[grammar.Variable, bool] = field(init=False, default_factory=dict)
    emit_exists      : bool                         = field(init=False, default=False)

    def analyze(
        self,
        program: grammar.Program
    ) -> tuple[grammar.Program, SymbolTable]:
        if (
            program.inputs is not None and
            len(program.function.parameters) == 0
        ):
             raise AnalysisError(
                  "Program supplies an input expression...",
                  program.inputs.location,
                  "",
                  "...but the defined function did not expect one.",
                  next(iter(program.function.parameters)).location
             )

        program.function = self.analyze_function(program.function)

        return program, self.symbol_table

    def analyze_function(self, function: grammar.Function) -> grammar.Function:
        self.symbol_table.update(function.parameters)
        self.bound_symbols.update(function.parameters.keys())

        function.body, stopped, _ = self.analyze_statement(function.body)

        if not stopped:
            raise AnalysisError(
                "Not all linear control paths in this function are termianted "
                "by a STOP statement.",
                function.location
            )

        return function

    def analyze_statement(
        self,
        statement: grammar.Statement
    ) -> tuple[grammar.Statement, bool, bool]:
        match statement:
            case grammar.Block(location, statements):
                if not statements:
                    raise AnalysisError(
                        "Found empty block.",
                        location
                    )

                new_statements = []
                for child_statement in statements:
                    new_child_statement, stopped, elide =\
                        self.analyze_statement(child_statement)

                    if not elide:
                        new_statements.append(new_child_statement)
                        if stopped:
                            break

                return (
                    replace(statement, statements=new_statements),
                    stopped,
                    len(new_statements) == 0
                )

            case grammar.Stop(_):
                for loop_label in self.loop_scope:
                    self.loop_stopped[loop_label] = True

                return statement, True, False

            case grammar.NoOp(_):
                return statement, False, True

            case grammar.Declaration(_, variables, type):
                for variable in variables:
                    if variable in self.symbol_table:
                        original_declaration = next(
                            _variable
                            for _variable in self.symbol_table
                            if _variable.identifier == variable.identifier
                        )
                        raise AnalysisError(
                            "Found declaration of variable "
                            f"{variable.identifier!r}...",
                            variable.location,
                            "",
                            "...that was already declared at.",
                            original_declaration.location
                        )
                    else:
                        self.symbol_table[variable] = type

                return statement, False, True

            case grammar.Assignment(_, variables, expression):
                self.analyze_expression(expression)

                for variable in variables:
                    self.analyze_variable_write(variable)

                return statement, False, False

            case grammar.Emit(_, variables):
                for variable in variables:
                    self.analyze_variable_read(variable)

                return statement, False, False

            case grammar.If(_, condition, truthy_branch, falsey_branch):
                self.analyze_variable_read(condition)

                truthy_branch, truthy_stopped, elide_truthy =\
                    self.analyze_statement(truthy_branch)

                falsey_branch, falsey_stopped, elide_falsey =\
                    self.analyze_statement(falsey_branch)

                return (
                    replace(
                        statement,
                        truthy_branch=
                            grammar.NoOp(truthy_branch.location)
                            if elide_truthy else truthy_branch,
                        falsey_branch=
                            grammar.NoOp(falsey_branch.location)
                            if elide_falsey else falsey_branch
                    ),
                    truthy_stopped and falsey_stopped,
                    elide_truthy and elide_falsey
                )

            case grammar.Loop(location, loop_label, body):
                if loop_label in self.loop_names:
                    original_introduction = next(
                        variable
                        for variable in self.loop_names
                        if variable.identifier == loop_label.identifier
                    )
                    raise AnalysisError(
                        "Found introduction of loop label "
                        f"{loop_label.identifier!r}...",
                        loop_label.location,
                        "",
                        "...that was already introduced at.",
                        original_introduction.location
                    )

                self.loop_names.add(loop_label)
                self.loop_scope.append(loop_label)
                self.loop_broken[loop_label] = False
                self.loop_stopped[loop_label] = False

                body, _, elide_body =\
                    self.analyze_statement(body)

                self.loop_scope.append(loop_label)
                if (
                    not self.loop_stopped[loop_label] and
                    not self.loop_broken[loop_label]
                ):
                    raise AnalysisError(
                        "Found loop containing neither a STOP statement nor "
                        "a BREAK statement referencing either this loop or any "
                        "of its parent loops.",
                        location,
                    )

                return statement, self.loop_stopped[loop_label], elide_body

            case grammar.Break(_, loop_label):
                if loop_label not in self.loop_scope:
                    raise AnalysisError(
                        "Found break to unintroduced loop label "
                        f"{loop_label.identifier!r}.",
                        loop_label.location
                    )

                for _loop_label in self.loop_scope[::-1]:
                    self.loop_broken[_loop_label] = True
                    if loop_label == _loop_label:
                        break

                return statement, False, False

            case grammar.Continue(_, loop_label):
                if loop_label not in self.loop_scope:
                    raise AnalysisError(
                        "Found continue to unintroduced loop label "
                        f"{loop_label.identifier!r}.",
                        loop_label.location
                    )

                return statement, False, False

            case _:
                raise AnalysisError(
                    "Found unknown statement.",
                    statement.location
                )

    def analyze_expression(self, expression: grammar.Expression):
        for variable in expression.free_variables:
            self.analyze_variable_read(variable)

    def analyze_variable_read(self, variable: grammar.Variable):
        if variable not in self.bound_symbols:
            raise AnalysisError(
                "Found read from uninitialised variable "
                f"{variable.identifier!r}.",
                variable.location
            )

    def analyze_variable_write(self, variable: grammar.Variable):
        if variable not in self.bound_symbols:
            if variable not in self.symbol_table:
                raise AnalysisError(
                    "Found write to undeclared variable "
                    f"{variable.identifier!r}.",
                    variable.location
                )
        self.bound_symbols.add(variable)
