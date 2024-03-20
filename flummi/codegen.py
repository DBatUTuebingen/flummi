from dataclasses import dataclass, field
from functools import partial
from itertools import chain


from . import CFG, grammar, sql, errors
from .utils import *
from .analyzer import SymbolTable
from .label_graph import *
from .data_flow import *


__all__ = (
    "codegen",
)


def codegen(
    graph: CFG.Graph,
    symbol_table: SymbolTable,
    program: grammar.Program,
    include_trace: bool = False,
    explicit_materialized: bool = False,
    avoid_multiple_recursive_references: bool = False,
    include_emit_order: bool = False,
    force_with_recursive: bool = False,
) -> str:
    return CodeGen(
        symbol_table,
        program,
        include_trace,
        explicit_materialized,
        avoid_multiple_recursive_references,
        include_emit_order,
        force_with_recursive,
    ).gen_program(graph)


class CodeGenError(errors.FlummiError, name="code generation"):
    ...


@dataclass
class CodeGen:
    symbol_table: SymbolTable
    program: grammar.Program
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

    def gen_expression(self, expression: grammar.Expression) -> str:
        try:
            return expression.source.format(*(
                f'({sql.variable(variable.identifier, "%input%")})'
                for variable in expression.free_variables
            ))
        except Exception as e:
            raise CodeGenError(
                "Encountered an error during formatting of an "
                "embedded SQL expression.",
                expression.location,
                "",
                "Given Query:",
                expression.source,
                "",
                "Error:",
                repr(e)
            ) from e

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


        state_columns = [
            variable.identifier
            for variable in self.jump_variables
        ]

        state_nulls = [
            sql.cast(sql.NULL, self.symbol_table[variable].source)
            for variable in self.jump_variables
        ]

        result_columns = [
            f'%result%{i}%'
            for i, _ in enumerate(self.emit_types)
        ]

        result_nulls = [
            sql.cast(sql.NULL, type.source)
            for type in self.emit_types
        ]

        working_table_columns = [
            "%kind%",
            "%label%",
            *state_columns,
            *result_columns
        ]

        if graph.initialising_assignment is not None:
            initial_state_expressions = [
                sql.cast(
                    f"({sql.variable(variable.identifier, "%init%")})"
                    if variable in graph.initialising_assignment.variables else
                    sql.NULL,
                    self.symbol_table[variable].source
                )
                for variable in self.jump_variables
            ]

            from_list=[
                sql.named(
                    f"({graph.initialising_assignment.expression.source})",
                    "%init%",
                    [
                        variable.identifier
                        for variable in graph.initialising_assignment.variables
                    ]
                )
            ]
        else:
            initial_state_expressions = [
                sql.cast(sql.NULL, self.symbol_table[variable].source)
                for variable in self.jump_variables
            ]
            from_list = []

        select_list = list(zipwith(sql.named,
            [
                sql.string("jump"),
                sql.string(graph.entry_label.label),
                *initial_state_expressions,
                *result_nulls
            ],
            working_table_columns
        ))

        block_ctes = [
            self.gen_block(graph.blocks[label])
            for label in dependent_ordering(collect_gotos(graph))
        ]

        if self.force_with_recursive or any(pred for pred in self.jump_predecessors.values()):
            collectors = []
            for label, block in graph.blocks.items():
                if CFG.contains_jumps(block):
                    select_list = list(zipwith(sql.named,
                        [
                            sql.string("jump"),
                            sql.name("%label%"),
                            *map(sql.name, state_columns),
                            *result_nulls
                        ],
                        working_table_columns
                    ))

                    collectors.append(
                        sql.select(
                            select_list=select_list,
                            from_list=[sql.name(label.label)],
                            predicates=['"%kind%"=\'jump\'']
                        )
                    )

                if CFG.contains_emits(block):
                    select_list = list(zipwith(sql.named,
                        [
                            sql.string("emit"),
                            sql.NULL,
                            *state_nulls,
                            *map(sql.name, result_columns)
                        ],
                        working_table_columns
                    ))

                    collectors.append(
                        sql.select(
                            select_list=select_list,
                            from_list=[sql.name(label.label)],
                            predicates=['"%kind%"=\'emit\'']
                        )
                    )

            if self.avoid_multiple_recursive_references:
                block_ctes = [
                    sql.cte(
                        name="%loop%",
                        columns=working_table_columns,
                        body="SELECT * FROM " + sql.variable("%loop%")
                    ),
                    *block_ctes
                ]

            return sql.with_ctes(
                ctes=[sql.cte(
                    name="%loop%",
                    columns=working_table_columns,
                    body=sql.union_all([
                        sql.select(select_list, from_list),
                        sql.with_ctes(
                            ctes=block_ctes,
                            body=sql.union_all(collectors)
                        )
                    ])
                )],
                body=sql.select(
                    select_list=[sql.name("%result%")],
                    from_list=[sql.name("%loop%")],
                    predicates=['"%kind%"=\'emit\'']
                )
            )
        else:
            collectors = []
            for label, block in graph.blocks.items():
                if CFG.contains_emits(block):
                    select_list = list(zipwith(sql.named,
                        [*map(sql.name, result_columns)],
                        result_columns
                    ))

                    collectors.append(
                        sql.select(
                            select_list=select_list,
                            from_list=[sql.name(label.label)],
                            predicates=['"%kind%"=\'emit\'']
                        )
                    )

            return sql.with_ctes(
                ctes=[
                    sql.cte(
                        name="%loop%",
                        columns=working_table_columns,
                        body=sql.select(select_list, from_list)
                    ),
                    *block_ctes
                ],
                body=sql.union_all(collectors)
            )

    def gen_block(self, block: CFG.Block) -> str:
        inputs = self.inputs[block.label]
        outputs = self.outputs[block.label]
        goto_predecessors = self.goto_predecessors[block.label]
        jump_predecessors = self.jump_predecessors[block.label]

        input_columns = [
            variable.identifier
            for variable in inputs
        ]

        output_columns = [
            variable.identifier
            for variable in outputs
        ]

        output_nulls = [
            sql.cast(sql.NULL, self.symbol_table[output].source)
            for output in outputs
        ]

        result_columns = [
            f'%result%{i}%'
            for i, _ in enumerate(self.emit_types)
        ]

        result_nulls = [
            sql.cast(sql.NULL, type.source)
            for type in self.emit_types
        ]

        emitted_vars = list(sorted(
            CFG.emited_variables(block),
            key=lambda emit_var: emit_var.identifier
        ))

        all_output_columns = ['%kind%', '%label%', *output_columns, *result_columns]

        select_list = [*map(sql.name, input_columns)] or [sql.NULL]

        row_sources = [
            sql.select(
                select_list=select_list,
                from_list=[f'"{predecessor.label}"'],
                predicates=['"%kind%"=\'goto\'', f'"%label%"=\'{block.label.label}\'']
            )
            for predecessor in goto_predecessors
        ]

        if jump_predecessors or self.entry_label == block.label:
            row_sources.append(
                sql.select(
                    select_list=select_list,
                    from_list=['"%loop%"'],
                    predicates=['"%kind%"=\'jump\'', f'"%label%"=\'{block.label.label}\'']
                )
            )

        ctes = [
            sql.cte(
                name='%inputs%',
                columns=input_columns or ['%'],
                materialize=self.explicit_materialized and bool(emitted_vars) and bool(block.assignments),
                body=sql.union_all(row_sources)
            )
        ]

        data_source = "%inputs%"

        if block.assignments:
            data_source = "%assign%"

            assignments = list(sorted(
                block.assignments,
                key=lambda assignment: assignment.variables
            ))

            scalar_assignments, multi_assignments =\
                partition(
                    assignments,
                    choice=lambda assignment: len(assignment.variables) == 1
                )

            assign_variables = [
                variable
                for assignment in assignments
                for variable in assignment.variables
            ]

            assign_columns = [
                variable.identifier
                for variable in assign_variables
            ]

            column_expressions = {
                variable: sql.cast(
                    self.gen_expression(assignment.expression),
                    self.symbol_table[variable].source
                )
                for assignment in scalar_assignments
                for variable in assignment.variables[:1]
            }

            from_list = ["%inputs%"]

            for i, assignment in enumerate(multi_assignments):
                row_variable = f'%assignment%{i}%'
                column_variables = [
                    variable.identifier
                    for variable in assignment.variables
                ]

                column_expressions.update(
                    (variable, sql.cast(
                        sql.name(expression),
                        self.symbol_table[variable].source
                    ))
                    for variable, expression in zip(
                        assignment.variables,
                        column_variables
                    )
                )

                from_list.append(
                    sql.named(
                        sql.lateral(self.gen_expression(assignment.expression)),
                        row_variable,
                        column_variables
                    )
                )

            select_list = list(zipwith(
                sql.named,
                (
                    column_expressions[variable]
                    for variable in assign_variables
                ),
                assign_columns
            ))

            ctes.append(
                sql.cte(
                    name='%assign%',
                    columns=assign_columns,
                    materialize=self.explicit_materialized and (len(block.terminals) > 1 or self.include_trace),
                    body=sql.select(select_list, from_list)
                )
            )

        row_generators = []
        for terminal in block.terminals:
            predicates = [*chain(
                (         sql.name(var.identifier) for var in terminal.truthy),
                ("NOT " + sql.name(var.identifier) for var in terminal.falsey),
            )]

            match terminal.type:
                case CFG.Emit(to_emit):
                    column_expressions = [
                        sql.string('emit'),
                        sql.NULL,
                        *output_nulls,
                    ]
                    for variable, type in zip(to_emit, self.emit_types):
                        column_expressions.append(sql.cast(sql.name(variable.identifier), type.source))

                case CFG.GoTo(label) | CFG.Jump(label):
                    column_expressions = [
                        sql.string('goto' if isinstance(terminal.type, CFG.GoTo) else 'jump'),
                        sql.name(label.label),
                        *map(sql.name, output_columns),
                        *result_nulls,
                    ]

                case _:
                    continue

            select_list = list(zipwith(
                sql.named,
                column_expressions,
                all_output_columns
            ))

            row_generators.append(
                sql.select(
                    select_list=select_list,
                    from_list=[f'"{data_source}"'],
                    predicates=predicates
                )
            )

        return sql.cte(
            name=block.label.label,
            columns=all_output_columns,
            materialize=self.explicit_materialized and (len(block.terminals) + self.include_trace > 1),
            body=sql.with_ctes(ctes, sql.union_all(row_generators))
        )
