from dataclasses import dataclass, field
from textwrap import dedent, indent
from typing import Generic, TypeVar, Iterator

from .algorithms import compute_loopless_successors, dependent_ordering
from .grammars import common, CFG


__all__ = (
    "codegen",
)


E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)


def _indent(lines: str, prefix: str):
    out = ""
    for i, line in enumerate(lines.splitlines(keepends=True)):
        if i > 0:
            out += prefix + line
        else:
            out += line
    return out


def codegen(graph: CFG.Graph) -> str:
    return CodeGen().gen_program(graph)


class CodeGenError(Exception):
    ...


@dataclass
class CodeGen(Generic[E, T]):
    row_source: str = field(init=False)
    control_columns: list[str] = field(init=False)
    scope_columns: list[str] = field(init=False)

    def gen_type(self, type: common.Type[T]) -> str:
        return str(type.source)

    def gen_expression(self, expression: common.Expression[E]) -> str:
        return f"""({_indent(expression.source.format(*(
            '"%sources%".' + self.gen_variable(variable)
            for variable in expression.free_variables
        )), ' ')})"""

    def gen_variable(self, variable: common.Variable) -> str:
        return f'"{variable.identifier}"'

    def gen_label(self, label: CFG.BlockLabel) -> str:
        return f'"{label.label}"'

    def gen_program(self, graph: CFG.Graph[E, T]) -> str:
        if graph.jumps:
            return self.gen_nonlinear_program(graph)
        else:
            return self.gen_linear_program(graph)

    def gen_linear_program(self, graph: CFG.Graph[E, T]) -> str:
        data_type = self.gen_type(graph.emits)

        input_variables = (
            ', ' * (0 < len(graph.inputs)) +
            ', '.join(
                self.gen_variable(variable)
                for variable in graph.blocks[graph.entry_label].parameters
            )
        )

        input_bindings = (
            (',\n' + ' '*19) * (0 < len(graph.inputs)) +
            ',\n'.join(
                indent(
                    self.gen_expression(graph.inputs[variable]) +
                    " :: " + self.gen_type(graph.variables[variable]) +
                    " AS " + self.gen_variable(variable),
                    ' ' * 19 * (i > 0)
                )
                for i, variable in enumerate(graph.blocks[graph.entry_label].parameters)
            )
        )

        self.row_source = '"%entrypoint%"'
        self.control_columns = ['"%kind%"', '"%result%"']
        self.scope_columns = [variable.identifier for variable in graph.blocks[graph.entry_label].parameters]

        blocks = indent(',\n'.join(
            self.gen_block(graph.blocks[label])
            for label in dependent_ordering(compute_loopless_successors(graph), graph.entry_label)
        ), ' ' * 10)[10:]

        emits = indent('\n  UNION ALL\n'.join(
            dedent(f"""
                SELECT "%result%"
                FROM   {self.gen_label(label)}
                WHERE  "%kind%" = 'data'
            """)[1:-1]
            for label, block in graph.blocks.items()
            if any(isinstance(statement, CFG.Emit) for statement in block.statements)
        ), ' ' * 8)[8:]

        return dedent(f"""
        WITH
          "%entrypoint%"("%kind%", "%result%"{input_variables}) AS (
            SELECT 'control', NULL :: {data_type}{input_bindings}
          ),
          {blocks}

        {emits};
        """)[1:-1]

    def gen_nonlinear_program(self, graph: CFG.Graph[E, T]) -> str:
        data_type = self.gen_type(graph.emits)

        trampolined_variables = (
            ', ' * (0 < len(graph.inputs)) +
            ', '.join(
                self.gen_variable(variable)
                for variable in graph.blocks[graph.entry_label].parameters
            )
        )

        input_bindings = (
            (',\n' + ' '*21) * (0 < len(graph.inputs)) +
            ',\n'.join(
                indent(
                    self.gen_expression(graph.inputs[variable]) +
                    " :: " + self.gen_type(graph.variables[variable]) +
                    " AS " + self.gen_variable(variable),
                    ' ' * 21 * (i > 0)
                )
                for i, variable in enumerate(graph.blocks[graph.entry_label].parameters)
            )
        )

        entry_label = graph.entry_label.label

        self.row_source = '"%trampoline%"'
        self.control_columns = ['"%kind%"', '"%result%"', '"%label%"']
        self.scope_columns = [variable.identifier for variable in graph.blocks[graph.entry_label].parameters]

        blocks = indent(',\n'.join(
            self.gen_block(graph.blocks[label])
            for label in dependent_ordering(compute_loopless_successors(graph), graph.entry_label)
        ), ' ' * 16)[16:]

        jumps = indent('\n  UNION ALL\n'.join(
            self.gen_jump(jump)
            for jump in graph.jumps
        ), ' ' * 14)[14:]

        emit_scope = (
          ', ' * (0 < len(graph.inputs)) +
          ', '.join(["NULL"] * len(graph.inputs))
        )
        emits = indent('\n  UNION ALL\n'.join(
            dedent(f"""
                SELECT "%kind%", "%result%", "%label%"{emit_scope}
                FROM   {self.gen_label(label)}
                WHERE  "%kind%" = 'data'
            """)[1:-1]
            for label, block in graph.blocks.items()
            if any(isinstance(statement, CFG.Emit) for statement in block.statements)
        ), ' ' * 14)[14:]


        return dedent(f"""
        WITH RECURSIVE
          "%trampoline%"("%kind%", "%result%", "%label%"{trampolined_variables}) AS (
            (
              SELECT 'control', NULL :: {data_type}, '{entry_label}'{input_bindings}
            )
              UNION ALL -- recursive union!
            (
              WITH
                {blocks}

              -- jumps
              {jumps}
                UNION ALL
              -- emits
              {emits}
            )
          )

        SELECT "%result%" FROM "%trampoline%" WHERE "%kind%" = 'data';
        """)[1:-1]

    def gen_jump(self, jump: CFG.JumpDirective) -> str:
        destination = jump.destination.label
        origin = self.gen_label(jump.origin)
        predicate = self.gen_predicate(jump.predicate)
        scope = (
            ', ' * (0 < len(jump.parameters)) +
            ', '.join(
                self.gen_variable(parameter)
                for parameter in jump.parameters
            )+
            ' ' * (0 < len(jump.parameters))
        )

        return dedent(f"""
            SELECT 'control', NULL, '{destination}'{scope}
            FROM   {origin}
            WHERE  "%kind%" = 'control'
            AND    {predicate}
        """)[1:-1]

    def gen_predicate(self, predicate: CFG.Predicate) -> str:
        match predicate:
            case CFG.Variable(variable):
                return f"{self.gen_variable(variable)} IS NOT DISTINCT FROM TRUE"
            case CFG.Not(operand):
                return f"NOT ({self.gen_predicate(operand)})"
            case CFG.And(left_operand, right_operand):
                return f"{self.gen_predicate(left_operand)} AND {self.gen_predicate(right_operand)}"
            case CFG.Tautology():
                return "TRUE"
            case _:
                raise CodeGenError("Unknown predicate form.")

    def conditional_variables(self, terminal: CFG.Terminal) -> list[common.Variable]:
        def iter(terminal: CFG.Terminal) -> Iterator[common.Variable]:
          match terminal:
              case CFG.If(condition, truthy_terminal, falsey_terminal):
                  yield condition
                  yield from self.conditional_variables(truthy_terminal)
                  yield from self.conditional_variables(falsey_terminal)
              case _:
                  return
        return list(iter(terminal))

    def output_parameter_variables(self, terminal: CFG.Terminal) -> list[common.Variable]:
        match terminal:
            case CFG.If(_, truthy_terminal, falsey_terminal):
                truthy_branch = self.output_parameter_variables(truthy_terminal)
                falsey_branch = self.output_parameter_variables(falsey_terminal)
                return truthy_branch + [
                    parameter
                    for parameter in falsey_branch
                    if parameter not in truthy_branch
                ]
            case CFG.GoTo(_, arguments) | CFG.Jump(_, arguments):
                return arguments
            case _:
                return []

    def gen_block(self, block: CFG.Block[E]) -> str:
        label = block.label.label

        control_columns = ', '.join(self.control_columns)

        input_scope_columns = (
            ', ' * (0 < len(block.parameters)) +
            ', '.join(
                self.gen_variable(parameter)
                for parameter in block.parameters
            )
        )

        output_parameter_variables = self.output_parameter_variables(block.terminal)
        conditional_variables = self.conditional_variables(block.terminal)

        actual_output_variables = output_parameter_variables + [
          parameter
          for parameter in conditional_variables
          if parameter not in output_parameter_variables
        ]

        assignments = {
            statement.variable: self.gen_expression(statement.expression)
            for statement in block.statements
            if isinstance(statement, CFG.Assignment)
        }

        output_columns = [
            f'{assignments.get(variable, self.gen_variable(variable))} AS "new%{variable.identifier}"'
            for variable in actual_output_variables
        ]

        output_columns = (
            (',\n' + ' '*19) * (0 < len(output_columns)) +
            ',\n'.join(
                [indent,_indent][i == 0](output_column, ' ' * 19)
                for i, output_column in enumerate(output_columns)
            )
        )

        emits = [
            statement
            for statement in block.statements
            if isinstance(statement, CFG.Emit)
        ]

        control = (
            indent(dedent(f"""
            SELECT 'control', NULL, NULL{output_columns}
            FROM   "%sources%"
            """)[1:[-1, None][0 < len(emits)]], ' ' * 10)[10:]
            if output_columns else ""
        )

        output_variables = (
            ', ' * (0 < len(actual_output_variables)) +
            ', '.join(
                self.gen_variable(variable)
                for variable in actual_output_variables
            )
        )

        sources = indent('\n  UNION ALL\n'.join(
            self.gen_reference(reference)
            for reference in block.predecessor_references
        ), ' ' * 14)[14:]

        emit_scope = _indent(
            ',\n' * (0 < len(actual_output_variables)) +
            ',\n'.join(["NULL"] * len(actual_output_variables)),
            ' '*23
        )
        emits = (
            ('\n'+' '*12+'UNION ALL\n\n') * (0 < len(emits)) * (0 < len(output_columns)) +
            indent('\n  UNION ALL\n'.join(
                dedent(f'''
                SELECT 'data',
                       {_indent(self.gen_expression(statement.to_emit), ' '*23)},
                       NULL{emit_scope}
                FROM   "%sources%"
                ''')[1:-1]
                for statement in emits
            ), ' ' * 10)[10 * (0 == len(output_columns)):]
        )


        return dedent(f"""
        "{label}"({control_columns}{output_variables}) AS (
          WITH
            "%sources%"({control_columns}{input_scope_columns}) AS (
              {sources}
            )

          {control}{emits}
        )
        """)[1:-1]

    def gen_reference(self, reference: CFG.Reference) -> str:
        match reference:
            case CFG.FromLoop(exepected_label):
                control_columns = ', '.join(self.control_columns)

                scope_columns = (
                    (',\n' + ' '*27) * (0 < len(self.scope_columns)) +
                    (',\n' + ' '*27).join(
                        f'"{column}"'
                        for column in self.scope_columns
                    )
                )

                exepected_label = exepected_label.label

                return dedent(f"""
                    SELECT {control_columns}{scope_columns}
                    FROM   {self.row_source}
                    WHERE  "%kind%" = 'control'
                    AND    "%label%" = '{exepected_label}'
                """)[1:-1]

            case CFG.FromBlock(label, arguments, predicate):
                control_columns = ', '.join(self.control_columns)

                arguments = (
                    (',\n' + ' '*27) * (0 < len(arguments)) +
                    (',\n' + ' '*27).join(
                        self.gen_variable(argument)
                        for argument in arguments
                    )
                )

                if isinstance(predicate, CFG.Tautology):
                    predicate = ""
                else:
                    predicate = '\n' + ' ' * 20 + f'AND    {self.gen_predicate(predicate)}'

                return dedent(f"""
                    SELECT {control_columns}{arguments}
                    FROM   {self.gen_label(label)}
                    WHERE  "%kind%" = 'control'{predicate}
                """)[1:-1]

            case _:
                raise CodeGenError("Unknown reference form.")
