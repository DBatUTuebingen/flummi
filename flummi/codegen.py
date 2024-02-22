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
    include_emit_order: bool = False,
    force_with_recursive: bool = False,
) -> str:
    return CodeGen(
        symbol_table,
        emit_type,
        variable_bindings,
        include_trace,
        explicit_materialized,
        avoid_multiple_recursive_references,
        include_emit_order,
        force_with_recursive,
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
    force_with_recursive: bool

    entry_label: CFG.BlockLabel = field(init=False)
    inputs: dict[CFG.BlockLabel, list[grammar.Variable]] = field(init=False)
    jump_predecessors: LabelGraph = field(init=False)
    goto_predecessors: LabelGraph = field(init=False)
    jump_variables: list[grammar.Variable] = field(init=False)
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
        self.jump_variables = list(sorted(unsorted_jump_variables, key=lambda variable: variable.identifier))
        self.inputs = {
            label: list(sorted(inputs, key=lambda variable: variable.identifier))
            for label, inputs in unsorted_inputs.items()
        }
        self.outputs = {
            label: list(sorted(outputs, key=lambda variable: variable.identifier))
            for label, outputs in compute_outputs(collect_successors(graph), unsorted_inputs).items()
        }

        if self.force_with_recursive or any(pred for pred in self.jump_predecessors.values()):
            return self.gen_program_with_jumps(graph)
        else:
            return self.gen_program_without_jumps(graph)

    def gen_program_without_jumps(self, graph: CFG.Graph) -> str:
        emit_sources = [
            label
            for label, block in graph.blocks.items()
            if CFG.contains_emits(block)
        ]

        working_table_columns_sql = (
            ', ' * (0 < len(self.jump_variables)) +
            ', '.join(
                self.gen_variable(variable)
                for variable in self.jump_variables
            )
        )

        working_table_nulls_sql = (
            ', ' * (0 < len(self.jump_variables)) +
            ', '.join(
                f"CAST(NULL AS {self.gen_type(self.symbol_table[variable])})"
                for variable in self.jump_variables
            )
        )

        initial_row_sql = _indent(
            ',\n'.join(
                f"CAST({self.gen_expression(self.variable_bindings[variable]) if variable in self.variable_bindings else "NULL"} AS {self.gen_type(self.symbol_table[variable])}) AS \"{variable.identifier}\""
                for variable in self.jump_variables
            ),
            ' ' * 19
        )

        blocks = _indent(',\n'.join(
            self.gen_block(graph.blocks[label])
            for label in dependent_ordering(collect_gotos(graph))
        ), ' ' * 11)

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
        WITH
          "%loop%"("%kind%", "%label%"{working_table_columns_sql}, "%result%"{trace_column_sql}{step_column_sql}{ordinaltiy_column_sql}) AS (
            SELECT 'jump' AS "%kind%",
                   '{graph.entry_label.label}' AS "%label%",
                   {initial_row_sql}{(',\n' + ' ' * 19) * bool(initial_row_sql)}CAST(NULL AS {self.emit_type_sql}) AS "%result%"{(',\n' + ' ' * 19) * (self.include_trace or self.include_emit_order)}{trace_null_column_sql}{(',\n' + ' ' * 20) * self.include_trace}{step_zero_column_sql}{', ' * (self.include_trace and self.include_emit_order)}{ordinaltiy_zero_column_sql}
           ),{blocks}

        {
           _indent(
               '\n  UNION ALL\n'.join(
                   chain(
                       (
                           dedent(
                               f"""
                               SELECT "%result%"{', ' * self.include_trace}{trace_null_column_sql}{', ' * self.include_trace}{step_null_column_sql}{ordinaltiy_column_sql}
                               FROM   "{label.label}"
                               WHERE  "%kind%"='emit'
                               """
                           )[1:-1]
                           for label in emit_sources
                       ),
                       (
                           dedent(
                               f"""
                               SELECT CAST(NULL AS {self.emit_type_sql}){trace_column_sql}{step_column_sql}{ordinaltiy_column_sql}
                               FROM   "{label.label}"
                               WHERE  "%kind%"='trace'
                               """
                           )[1:-1]
                           for label in graph.blocks
                           if self.include_trace
                       )
                   )
               ),
               ' ' * 8
           )
        };
        """)[1:-1]

    def gen_program_with_jumps(self, graph: CFG.Graph) -> str:
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
            ', ' * (0 < len(self.jump_variables)) +
            ', '.join(
                self.gen_variable(variable)
                for variable in self.jump_variables
            )
        )

        working_table_nulls_sql = (
            ', ' * (0 < len(self.jump_variables)) +
            ', '.join(
                f"CAST(NULL AS {self.gen_type(self.symbol_table[variable])})"
                for variable in self.jump_variables
            )
        )

        initial_row_sql = _indent(
            ',\n'.join(
                f"CAST({self.gen_expression(self.variable_bindings[variable]) if variable in self.variable_bindings else "NULL"} AS {self.gen_type(self.symbol_table[variable])}) AS \"{variable.identifier}\""
                for variable in self.jump_variables
            ),
            ' ' * 20
        )

        blocks = _indent(',\n'.join(
            self.gen_block(graph.blocks[label])
            for label in dependent_ordering(collect_gotos(graph))
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
        outputs = self.outputs[block.label]
        goto_predecessors = self.goto_predecessors[block.label]
        jump_predecessors = self.jump_predecessors[block.label]

        input_columns = [
            self.gen_variable(variable)
            for variable in inputs
        ]

        output_columns = [
            self.gen_variable(variable)
            for variable in outputs
        ]

        output_nulls = [
            f"CAST(NULL AS {self.gen_type(self.symbol_table[output])})"
            for output in outputs
        ]

        assignments = list(sorted(
            block.assignments,
            key=lambda assignment: assignment.variable.identifier
        ))

        emitted_vars = list(sorted(
            CFG.emited_variables(block),
            key=lambda emit_var: emit_var.identifier
        ))

        assign_columns = [
            self.gen_variable(assignment.variable)
            for assignment in assignments
        ]

        auxiliary_output_columns = []
        auxiliary_input_columns = []

        if self.include_trace:
            auxiliary_input_columns.append('"%step%"')
            auxiliary_output_columns.append('"%trace%"')
            auxiliary_output_columns.append('"%step%"')

        if self.include_emit_order:
            auxiliary_input_columns.append('"%ordinality%"')
            auxiliary_output_columns.append('"%ordinality%"')

        row_sources = [
            dedent(
                f"""\
                SELECT {_indent(',\n'.join(input_columns or ["NULL"]), ' ' * 23)}
                FROM   "{predecessor.label}"
                WHERE  "%kind%"='goto'
                AND    "%label%"='{block.label.label}'
                """
            ).strip()
            for predecessor in goto_predecessors
        ]

        if jump_predecessors or self.entry_label == block.label:
            row_sources.append(dedent(
                f"""\
                SELECT {_indent(',\n'.join(input_columns or ["NULL"]), ' ' * 23)}
                FROM   "%loop%"
                WHERE  "%kind%"='jump'
                AND    "%label%"='{block.label.label}'
                """
            ).strip())

        data_source = "%assign%" if assignments else "%inputs%"
        all_output_columns = ['"%kind%"', '"%label%"', *output_columns, '"%result%"', *auxiliary_output_columns]

        row_generators = []
        emit_count = 0
        for terminal in block.terminals:
            predicate = ("\nWHERE  " + "\nAND    ".join(chain(
                (         self.gen_variable(var) for var in terminal.truthy),
                ("NOT " + self.gen_variable(var) for var in terminal.falsey),
            ))) * bool(terminal.truthy or terminal.falsey)

            match terminal.type:
                case CFG.Emit(to_emit):
                    columns = [
                        "'emit'",
                        "NULL",
                        *output_nulls,
                        f"CAST({_indent(self.gen_variable(to_emit), ' ' * 5)} AS {self.emit_type_sql})"
                    ]
                    if self.include_trace:
                        columns.append("CAST(NULL AS json)")
                        columns.append("CAST(NULL AS int)")
                    if self.include_emit_order:
                        emit_count += 1
                        columns.append(f'"%ordinality%" + {emit_count}')

                case CFG.GoTo(label) | CFG.Jump(label):
                    columns = [
                        "'goto'" if isinstance(terminal.type, CFG.GoTo) else "'jump'",
                        f"'{label.label}'",
                        *output_columns,
                        f"CAST(NULL AS {self.emit_type_sql})"
                    ]
                    if self.include_trace:
                        columns.append("CAST(NULL AS json)")
                        columns.append('"%step%" + 1')
                    if self.include_emit_order:
                        columns.append(f'"%ordinality%" + {len(emitted_vars)}')

                case _:
                    continue

            row_generators.append(dedent(
                f"""\
                SELECT {_indent(',\n'.join(f"{var} AS {name}" for var, name in zip(columns, all_output_columns)), ' ' * 23)}
                FROM   "{data_source}"
                """
            ).strip() + predicate)

        if self.include_trace:
            for terminal in block.terminals:
                predicate = ("\nWHERE  " + "\nAND    ".join(chain(
                    (         self.gen_variable(var) for var in terminal.truthy),
                    ("NOT " + self.gen_variable(var) for var in terminal.falsey),
                ))) * bool(terminal.truthy or terminal.falsey)

                match terminal.type:
                    case CFG.GoTo(label) | CFG.Jump(label):
                        columns = [
                            "'trace'",
                            f"'{block.label.label}'",
                            *output_nulls,
                            f"CAST(NULL AS {self.emit_type_sql})",
                            dedent(f"""\
                                json_object(
                                  '%kind%' VALUE '{"goto" if isinstance(terminal.type, CFG.GoTo) else "jump"}',
                                  '%label%' VALUE '{label.label}',
                                  {
                                    _indent(
                                        ",\n".join(
                                            f"'{assignment.variable.identifier}' VALUE {self.gen_variable(assignment.variable)}"
                                            for assignment in assignments
                                        ),
                                        ' ' * 34
                                    )
                                  }
                                )
                            """).strip(),
                            '"%step%"'
                        ]
                        if self.include_emit_order:
                            columns.append(f'"%ordinality%"')

                    case _:
                        continue

                row_generators.append(dedent(
                    f"""\
                    SELECT {_indent(',\n'.join(f"{var} AS {name}" for var, name in zip(columns, all_output_columns)), ' ' * 27)}
                    FROM   "{data_source}"
                    """
                ).strip() + predicate)

        return dedent(f"""\
        "{block.label.label}"({", ".join(all_output_columns)}) AS{" MATERIALIZED" * (self.explicit_materialized and (len(block.terminals) + self.include_trace > 1))} (
          WITH
            "%inputs%"({', '.join([*input_columns, *auxiliary_input_columns] or ['"%"'])}) AS{" MATERIALIZED" * (self.explicit_materialized and bool(emitted_vars) and bool(assignments))} (
              {_indent("\n  UNION ALL\n".join(row_sources), ' ' * 14)}
            ){
                _indent(
                    ",\n" +
                    dedent(
                        f"""
                        "%assign%"({", ".join([*assign_columns, *auxiliary_input_columns])}) AS{" MATERIALIZED" * (self.explicit_materialized and (len(block.terminals) > 1 or self.include_trace))} (
                          SELECT {
                                    _indent(
                                        ",\n".join(
                                            f'CAST({_indent(self.gen_expression(assignment.expression), ' ' * 5)} AS {self.gen_type(self.symbol_table[assignment.variable])}) AS {self.gen_variable(assignment.variable)}'
                                            for assignment in assignments
                                        ),
                                        ' ' * 33
                                    )
                                 }{(',\n' + ' ' * 33 + '"%step%"') * self.include_trace}{(',\n' + ' ' * 33 + '"%ordinality%"') * self.include_emit_order}
                          FROM   "%inputs%"
                        )
                        """[1:]
                    ),
                    ' ' * 12
                ) * bool(assignments)
            }
          {_indent("\n  UNION ALL\n".join(row_generators), " " * 10)}
        )
        """).strip()
