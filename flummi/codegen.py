from dataclasses import dataclass, field, InitVar
from itertools import chain
from textwrap import dedent, indent


from . import CFG, grammar
from .analyzer import SymbolTable, VariableBindings
from .label_graph import *
from .data_flow import *

__all__ = (
    "codegen",
)


def _indent(lines: str, prefix: str):
    out = ""
    for i, line in enumerate(lines.splitlines(keepends=True)):
        if i > 0:
            out += prefix + line
        else:
            out += line
    return out


def codegen(
    graph: CFG.Graph,
    symbol_table: SymbolTable,
    emit_type: grammar.Type,
    variable_bindings: VariableBindings,
    include_trace: bool = False,
    explicit_materialized: bool = False,
    avoid_multiple_recursive_references: bool = False,
    include_emit_order: bool = False
) -> str:
    return CodeGen(
        symbol_table,
        emit_type,
        variable_bindings,
        include_trace,
        explicit_materialized,
        avoid_multiple_recursive_references,
        include_emit_order
    ).gen_program(graph)


class CodeGenError(Exception):
    ...


@dataclass
class CodeGen:
    symbol_table: SymbolTable
    emit_type: InitVar[grammar.Type]
    variable_bindings: VariableBindings
    include_trace: bool
    explicit_materialized: bool
    avoid_multiple_recursive_references: bool
    include_emit_order: bool

    entry_label: CFG.BlockLabel = field(init=False)
    inputs: dict[CFG.BlockLabel, list[grammar.Variable]] = field(init=False)
    jump_predecessors: LabelGraph = field(init=False)
    goto_predecessors: LabelGraph = field(init=False)
    emit_type_sql: str = field(init=False)
    condition_variable_counter: int = field(init=False, default=0)

    def __post_init__(self, emit_type: grammar.Type):
        self.emit_type_sql = self.gen_type(emit_type)

    def gen_type(self, type: grammar.Type) -> str:
        return str(type.source)

    def gen_expression(self, expression: grammar.Expression) -> str:
        return f"""({_indent(expression.source.format(*(
            f'("%inputs%".{self.gen_variable(variable)})'
            for variable in expression.free_variables
        )), ' ')})"""

    def gen_variable(self, variable: grammar.Variable) -> str:
        return f'"{variable.identifier}"'

    def gen_label(self, label: CFG.BlockLabel) -> str:
        return f'"{label.label}"'

    def gen_program(self, graph: CFG.Graph) -> str:
        self.entry_label = graph.entry_label

        self.jump_predecessors = invert_label_graph(collect_jumps(graph))
        self.goto_predecessors = invert_label_graph(collect_gotos(graph))
        unsorted_inputs, unsorted_jump_variables = get_block_inputs(graph)
        jump_variables = list(sorted(unsorted_jump_variables, key=lambda variable: variable.identifier))
        self.inputs = {
            label: list(sorted(inputs, key=lambda variable: variable.identifier))
            for label, inputs in unsorted_inputs.items()
        }


        jump_sources = [
            label
            for label, block in graph.blocks.items()
            if CFG.contains_jumps(block)
        ]

        emit_sources = [
            label
            for label, block in graph.blocks.items()
            if CFG.contains_emits(block)
        ]

        working_table_columns_sql = (
            ', ' * (0 < len(jump_variables)) +
            ', '.join(
                self.gen_variable(variable)
                for variable in jump_variables
            )
        )

        working_table_nulls_sql = (
            ', ' * (0 < len(jump_variables)) +
            ', '.join(
                f"CAST(NULL AS {self.gen_type(self.symbol_table[variable])})"
                for variable in jump_variables
            )
        )

        initial_row_sql = _indent(
            ',\n'.join(
                f"CAST({self.gen_expression(self.variable_bindings[variable]) if variable in self.variable_bindings else "NULL"} AS {self.gen_type(self.symbol_table[variable])}) AS \"{variable.identifier}\""
                for variable in jump_variables
            ),
            ' ' * 20
        )

        blocks = _indent(',\n'.join(
            self.gen_block(graph.blocks[label])
            for label in sorted(dependent_ordering(collect_gotos(graph)), key=lambda label: label.label)
        ), ' ' * 14)

        trace_column_sql = (
            ', "%trace%"'
            if self.include_trace else
            ""
        )

        trace_null_column_sql = (
            'CAST(NULL AS json) AS "%trace%"'
            if self.include_trace else
            ""
        )

        step_column_sql = (
            ', "%step%"'
            if self.include_trace else
            ""
        )

        step_zero_column_sql = (
            'CAST(0 AS int) AS "%step%"'
            if self.include_trace else
            ""
        )

        step_null_column_sql = (
            'CAST(NULL AS int) AS "%step%"'
            if self.include_trace else
            ""
        )

        ordinaltiy_column_sql = (
            ', "%ordinality%"'
            if self.include_emit_order else
            ""
        )

        ordinaltiy_zero_column_sql = (
            'CAST(0 AS int) AS "%ordinality%"'
            if self.include_emit_order else
            ""
        )

        return dedent(f"""
        WITH RECURSIVE
          "%loop%"("%kind%", "%label%"{working_table_columns_sql}, "%result%"{trace_column_sql}{step_column_sql}{ordinaltiy_column_sql}) AS (
            (SELECT 'jump' AS "%kind%",
                    '{graph.entry_label.label}' AS "%label%",
                    {initial_row_sql}{(',\n' + ' ' * 20) * bool(initial_row_sql)}CAST(NULL AS {self.emit_type_sql}) AS "%result%"{(',\n' + ' ' * 20) * (self.include_trace or self.include_emit_order)}{trace_null_column_sql}{(',\n' + ' ' * 20) * self.include_trace}{step_zero_column_sql}{', ' * (self.include_trace and self.include_emit_order)}{ordinaltiy_zero_column_sql})
              UNION ALL -- recursive union!
            (WITH
              {
                _indent(
                    dedent(
                        f"""
                        "%loop%"("%kind%", "%label%"{working_table_columns_sql}, "%result%"{trace_column_sql}{ordinaltiy_column_sql}) AS{" MATERIALIZED" * self.explicit_materialized} (
                          SELECT * FROM "%loop%"
                        ),
                        """[1:]
                    ),
                    ' ' * 14
                ) * self.avoid_multiple_recursive_references
              }{(' ' * 14) * self.avoid_multiple_recursive_references}{blocks}

             {
                _indent(
                    '\n  UNION ALL\n'.join(
                        chain(
                            (
                                dedent(
                                    f"""
                                    SELECT 'jump', "%label%"{working_table_columns_sql}, CAST(NULL AS {self.emit_type_sql}){', ' * self.include_trace}{trace_null_column_sql}{step_column_sql}{ordinaltiy_column_sql}
                                    FROM   "{label.label}"
                                    WHERE  "%kind%"='jump'
                                    """
                                )[1:-1]
                                for label in jump_sources
                            ),
                            (
                                dedent(
                                    f"""
                                    SELECT 'emit', NULL{working_table_nulls_sql}, "%result%"{', ' * self.include_trace}{trace_null_column_sql}{', ' * self.include_trace}{step_null_column_sql}{ordinaltiy_column_sql}
                                    FROM   "{label.label}"
                                    WHERE  "%kind%"='emit'
                                    """
                                )[1:-1]
                                for label in emit_sources
                            ),
                            (
                                dedent(
                                    f"""
                                    SELECT 'trace', "%label%"{working_table_nulls_sql}, CAST(NULL AS {self.emit_type_sql}){trace_column_sql}{step_column_sql}{ordinaltiy_column_sql}
                                    FROM   "{label.label}"
                                    WHERE  "%kind%"='trace'
                                    """
                                )[1:-1]
                                for label in graph.blocks
                                if self.include_trace
                            )
                        )
                    ),
                    ' ' * 13
                )
             }
            )
          )

        SELECT "%result%"{', "%ordinality%"' * self.include_emit_order} FROM "%loop%" WHERE "%kind%"='emit';
        """)[1:-1]

    def gen_block(self, block: CFG.Block) -> str:
        inputs = self.inputs[block.label]
        goto_predecessors = self.goto_predecessors[block.label]
        jump_predecessors = self.jump_predecessors[block.label]

        unsorted_successor_info, conditional_variable_bindings = self.destructure_terminal(block.terminal)
        successor_info = list(sorted(unsorted_successor_info))

        input_columns_sql = (
            ', '.join(
                self.gen_variable(variable)
                for variable in inputs
            )
        )

        assignments = list(sorted(
            (
                statement
                for statement in block.statements
                if isinstance(statement, CFG.Assignment)
            ),
            key=lambda assignment: assignment.variable.identifier
        ))

        emits = list(sorted(
            (
                statement
                for statement in block.statements
                if isinstance(statement, CFG.Emit)
            ),
            key=lambda emit: emit.to_emit.free_variables
        ))

        assign_columns_sql = (
            ', '.join(
                self.gen_variable(assignment.variable)
                for assignment in chain(assignments, conditional_variable_bindings)
            )
        )

        output_columns_sql = (
            ', ' * bool(assignments) +
            ', '.join(
                self.gen_variable(assignment.variable)
                for assignment in assignments
            )
        )

        output_nulls_sql = (
            ', ' * bool(assignments) +
            ', '.join(
                f"CAST(NULL AS {self.gen_type(self.symbol_table[assignment.variable])})"
                for assignment in assignments
            )
        )

        trace_column_sql = (
            ', "%trace%"'
            if self.include_trace else
            ""
        )

        step_column_sql = (
            ', "%step%"'
            if self.include_trace else
            ""
        )

        trace_null_column_sql = (
            ", CAST(NULL AS json)"
            if self.include_trace else
            ""
        )

        step_null_column_sql = (
            ", CAST(NULL AS int)"
            if self.include_trace else
            ""
        )

        ordinality_column_sql = (
            ', "%ordinality%"'
            if self.include_emit_order else
            ""
        )

        next_ordinality_column_sql = (
            f', "%ordinality%" + CAST({len(emits)} AS int)'
            if self.include_emit_order else
            ""
        )

        return dedent(f"""
        "{block.label.label}"("%kind%", "%label%"{output_columns_sql}, "%result%"{trace_column_sql}{step_column_sql}{ordinality_column_sql}) AS{" MATERIALIZED" * (self.explicit_materialized and (len(successor_info) + len(emits) + self.include_trace > 1))} (
          WITH
            "%inputs%"({input_columns_sql or '"%"'}{step_column_sql}{ordinality_column_sql}) AS{" MATERIALIZED" * (self.explicit_materialized and bool(emits) and bool(assignments))} (
              {
                _indent(
                    "\n  UNION ALL\n".join(
                        chain(
                            [
                                dedent(
                                    f"""
                                    SELECT {input_columns_sql or 'NULL'}{step_column_sql}{ordinality_column_sql}
                                    FROM   "%loop%"
                                    WHERE  "%kind%"='jump'
                                    AND    "%label%"='{block.label.label}'
                                    """
                                )[1:-1]
                            ] * (bool(jump_predecessors) or self.entry_label == block.label),
                            (
                                dedent(
                                    f"""
                                    SELECT {input_columns_sql or 'NULL'}{step_column_sql}{ordinality_column_sql}
                                    FROM   "{parent_label.label}"
                                    WHERE  "%kind%"='goto'
                                    AND    "%label%"='{block.label.label}'
                                    """
                                )[1:-1]
                                for parent_label in goto_predecessors
                            )
                        )
                    ),
                    ' ' * 14
                )
              }
            ){
                _indent(
                    ",\n" +
                    dedent(
                        f"""
                        "%assign%"({assign_columns_sql}{step_column_sql}{ordinality_column_sql}) AS{" MATERIALIZED" * (self.explicit_materialized and (len(successor_info) > 1 or self.include_trace))} (
                          SELECT {
                                    _indent(
                                        ",\n".join(
                                            f'CAST({_indent(self.gen_expression(assignment.expression), ' ' * 5)} AS {self.gen_type(self.symbol_table[assignment.variable])}) AS {self.gen_variable(assignment.variable)}'
                                            for assignment in chain(assignments, conditional_variable_bindings)
                                        ),
                                        ' ' * 33
                                    )
                                 }{(',\n' + ' ' * 33 + '"%step%"') * self.include_trace}{(',\n' + ' ' * 33 + '"%ordinality%"') * self.include_emit_order}
                          FROM "%inputs%"
                        )
                        """[1:]
                    ),
                    ' ' * 12
                ) * (bool(assignments) or bool(conditional_variable_bindings))
            }
          {
            _indent(
               "\n  UNION ALL\n".join(
                    chain(
                        (
                            dedent(
                                f"""
                                SELECT {kind}, {label}{output_columns_sql}, CAST(NULL AS {self.emit_type_sql}){trace_null_column_sql}{step_null_column_sql}{next_ordinality_column_sql}
                                FROM   "%assign%"
                                WHERE  {predicate}
                                """
                            )[1:-1]
                            for kind, label, predicate in successor_info
                        ),
                        (
                            dedent(
                                f"""
                                SELECT 'emit', NULL{output_nulls_sql},
                                       CAST({_indent(self.gen_expression(emit.to_emit), ' ' * 45)} AS {self.emit_type_sql}){trace_null_column_sql}{step_null_column_sql}{ordinality_column_sql}
                                FROM   "%inputs%"
                                """
                            )[1:-1]
                            for emit in emits
                        ),
                        [
                            dedent(
                                f"""
                                SELECT 'trace', '{block.label.label}'{output_nulls_sql}, CAST(NULL AS {self.emit_type_sql}),
                                        json_object(
                                          '%kind%' VALUE {kind},
                                          '%label%' VALUE {label},
                                          {
                                            _indent(
                                                ",\n".join(
                                                    f"'{assignment.variable.identifier}' VALUE {self.gen_variable(assignment.variable)}"
                                                    for assignment in assignments
                                                ),
                                                ' ' * 42
                                            )
                                          }
                                       ) AS "%trace%",
                                       "%step%"{(',\n' + ' ' * 39 + 'CAST(NULL AS int)') * self.include_emit_order}
                                FROM   "%assign%"
                                WHERE  {predicate}
                                """
                            )[1:-1]
                            for kind, label, predicate in successor_info
                        ] * self.include_trace
                    )
                ),
                " " * 10
            )
          }
        )
        """)[1:-1]

    def destructure_terminal(self, terminal: CFG.Terminal, predicate: str = "TRUE") -> tuple[set[tuple[str,str,str]], list[CFG.Assignment]]:
        match terminal:
            case CFG.Stop():
                return set(), []
            case CFG.GoTo(label):
                return {("'goto'",f"'{label.label}'",predicate)}, []
            case CFG.Jump(label):
                return {("'jump'",f"'{label.label}'",predicate)}, []
            case CFG.If(expression, truthy, falsey):
                var = f"condition%{self.condition_variable_counter}"
                self.symbol_table[grammar.Variable(var)] = grammar.Type("bool")
                self.condition_variable_counter += 1
                truthy_branches, truthy_bindings = self.destructure_terminal(truthy, f'{predicate} AND "{var}"')
                falsey_branches, falsey_bindings = self.destructure_terminal(falsey, f'{predicate} AND NOT "{var}"')
                return truthy_branches | falsey_branches, [CFG.Assignment(grammar.Variable(var), expression), *truthy_bindings, *falsey_bindings]
            case _:
                raise TypeError(f"Unexpected kind of terminal: {terminal}")
