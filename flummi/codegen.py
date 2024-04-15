from itertools import chain

from .IR import CFG

from . import sql, errors, lowering
from .utils import *
from .analyzer import SymbolTable
from .label_graph import *
from .data_flow import *


__all__ = (
    "codegen",
)


class CodeGenError(errors.FlummiError, name="code generation"):
    ...


def codegen(
    program: lowering.Program,
    symbol_table: SymbolTable
) -> sql.SQL:
    constant_control_columns = [
        "%function%",
        "%caller%",
        "%handle%",
        "%depth%",
    ]

    constant_control_column_types = [
        "text",
        "text",
        "text",
        "int",
    ]

    variable_control_columns = [
        "%kind%",
        "%label%",
    ]

    variable_control_column_types = [
        "text",
        "text",
    ]

    function_CTEs = []
    program_collector_data: list[tuple[str, set[str], dict[str, str]]] = []

    for function in program.function_list:
        graph = function.body
        input_variables = get_block_inputs(graph)
        output_variables = compute_outputs(
            collect_successors(graph),
            input_variables
        )
        block_CTEs = []
        function_collector_data: list[tuple[set[str], str]] = []
        function_loop_carried_variables: set[lowering.Identifier] = set()
        calls_in_function = set()

        block_goto_predecessors = invert_label_graph(collect_gotos(graph))
        block_jump_predecessors = invert_label_graph(collect_jumps(graph))

        block_calls = {
            terminal.type.handle: terminal.type.target
            for block in graph.blocks.values()
            for terminal in block.terminals
            if isinstance(terminal.type, CFG.Call)
        }

        for label in dependent_ordering(collect_gotos(graph)):
            block = graph.blocks[label]
            input_columns = [
                *constant_control_columns,
                *sorted(
                    variable.identifier
                    for variable in input_variables[label]
                )
            ]

            step_ctes = []

            sources: list[tuple[str, str]] = [
                ('goto', predecessor.identifier)
                for predecessor in block_goto_predecessors[label]
            ]

            if label == graph.entry_label:
                sources.append(('call', "%loop%"))

            if block_jump_predecessors[label]:
                sources.append(('jump', "%loop%"))

            if isinstance(block.action, CFG.Waits):
                sources.append(('wait', "%loop%"))

            step_ctes.append(
                sql.cte(
                    name="%inputs%",
                    columns=input_columns,
                    body=sql.union_all(
                        sql.select(
                            select_list=[
                                sql.variable(column, table)
                                for column in input_columns
                            ],
                            from_list=[sql.name(table)],
                            predicates=[
                                f"{sql.variable("%function%", table)} = "
                                f"{sql.string(function.name.identifier)}",
                                f"{sql.variable("%kind%", table)} = "
                                f"{sql.string(kind)}",
                                f"{sql.variable("%label%", table)} = "
                                f"{sql.string(label.identifier)}",
                            ]
                        )
                        for kind, table in sources
                    )
                )
            )

            collector_source = "%inputs%"
            additional_collector_predicates = []
            block_collector_data: list[tuple[dict[str, sql.SQL], list[sql.SQL]]] = []

            match block.action:
                case CFG.Assignments(assignments):
                    assignment_columns = [
                        *constant_control_columns,
                        *sorted({
                            *(
                                variable.identifier
                                for variable in output_variables[label]
                            ),
                            *(
                                variable.identifier
                                for assignment in assignments
                                for variable in assignment.variables
                            )
                        })
                    ]

                    assignment_column_expressions = {}

                    scalar_assignments, multi_assignments =\
                        partition(
                            assignments,
                            choice=lambda assignment: len(assignment.variables) == 1
                        )

                    for assignment in scalar_assignments:
                        variable, *_ = assignment.variables
                        assignment_column_expressions[variable.identifier] =\
                            sql.cast(
                                gen_expression(
                                    assignment.expression,
                                    rowvar=collector_source
                                ),
                                symbol_table[variable].source
                            )

                    lateral_joins = []

                    for i, assignment in enumerate(multi_assignments):
                        row_variable = f'%assignment%{i}%'
                        column_variables = [
                            variable.identifier
                            for variable in assignment.variables
                        ]

                        assignment_column_expressions.update(
                            (
                                variable.identifier,
                                sql.cast(
                                    sql.name(expression),
                                    symbol_table[variable].source
                                )
                            )
                            for variable, expression in zip(
                                assignment.variables,
                                column_variables
                            )
                        )

                        lateral_joins.append(
                            sql.named(
                                sql.lateral(gen_expression(
                                    assignment.expression,
                                    rowvar=collector_source
                                )),
                                row_variable,
                                column_variables
                            )
                        )

                    step_ctes.append(
                        sql.cte(
                            name="%assign%",
                            columns=assignment_columns,
                            body=sql.select(
                                select_list=[
                                    sql.named(
                                        assignment_column_expressions.get(
                                            column,
                                            sql.variable(column, collector_source)
                                        ),
                                        column
                                    )
                                    for column in assignment_columns
                                ],
                                from_list=[
                                    sql.name(collector_source),
                                    *lateral_joins
                                ]
                            )
                        )
                    )

                    collector_source = "%assign%"

                case CFG.Waits(waits):
                    wait_columns = [
                        *constant_control_columns,
                        "done?",
                        *sorted(
                            variable.identifier
                            for variable in output_variables[label]
                        )
                    ]

                    left_outer_joins = []
                    done_checks = []
                    wait_column_expressions = {}

                    for wait in waits:
                        table_alias = wait.handle.identifier
                        associated_function = program.functions[block_calls[wait.handle]]
                        left_outer_joins.append(
                            sql.join(
                                type="LEFT OUTER",
                                table=sql.named(
                                    sql.name("%loop%"),
                                    table_alias
                                ),
                                predicates=[
                                    f"{sql.variable("%function%", collector_source)} = "
                                    f"{sql.variable("%caller%", table_alias)}",
                                    f"{sql.string(wait.handle.identifier)} = "
                                    f"{sql.variable("%handle%", table_alias)}",
                                    f"{sql.variable("%depth%", collector_source)} = "
                                    f"{sql.variable("%depth%", table_alias)} - 1",
                                    f"{sql.string("return")} = "
                                    f"{sql.variable("%kind%", table_alias)}",
                                ]
                            )
                        )
                        done_checks.append(
                            f"{sql.variable("%kind%", wait.handle.identifier)} "\
                            "IS NOT NULL"
                        )
                        wait_column_expressions.update({
                            target.identifier: sql.variable(
                                result_column,
                                table_alias
                            )
                            for result_column, target in zip(
                                (
                                    f"{associated_function.name.identifier}%result#{i}"
                                    for i, _ in enumerate(
                                        associated_function.return_types
                                    )
                                ),
                                wait.targets
                            )
                        })

                    wait_column_expressions["done?"] =\
                        sql.paren(" AND ".join(done_checks))

                    step_ctes.append(
                        sql.cte(
                            name="%wait%",
                            columns=wait_columns,
                            body=sql.select(
                                select_list=[
                                    sql.named(
                                        wait_column_expressions.get(
                                            column,
                                            sql.variable(column, collector_source)
                                        ),
                                        column
                                    )
                                    for column in wait_columns
                                ],
                                from_list=[sql.name(collector_source)],
                                join_list=left_outer_joins
                            )
                        )
                    )

                    collector_source = "%wait%"
                    additional_collector_predicates.append(
                        f"{sql.variable("done?", "%wait%")}"
                    )

                    block_collector_data.append((
                        {
                            "%function%": sql.variable("%function%", collector_source),
                            "%caller%": sql.variable("%caller%", collector_source),
                            "%handle%": sql.variable("%handle%", collector_source),
                            "%depth%": sql.variable("%depth%", collector_source),
                            "%kind%": sql.string('wait'),
                            "%label%": sql.string(label.identifier),
                            **{
                                variable.identifier: sql.variable(variable.identifier, collector_source)
                                for variable in output_variables[label]
                            },
                        },
                        [f"NOT {sql.variable("done?", "%wait%")}"]
                    ))

                case _:
                    ...

            contains_return = False
            calls_in_block = set()

            for terminal in block.terminals:
                predicates = [*chain(
                    additional_collector_predicates,
                    (         sql.variable(var.identifier, collector_source) for var in terminal.truthy),
                    ("NOT " + sql.variable(var.identifier, collector_source) for var in terminal.falsey),
                )]

                collector_column_expressions = {}
                match terminal.type:
                    case CFG.GoTo(target) | CFG.Jump(target):
                        if isinstance(terminal.type, CFG.GoTo):
                            kind = 'goto'
                        else:
                            kind = 'jump'
                            function_loop_carried_variables.update(
                                input_variables[target]
                            )

                        collector_column_expressions.update({
                            "%function%": sql.variable("%function%", collector_source),
                            "%caller%": sql.variable("%caller%", collector_source),
                            "%handle%": sql.variable("%handle%", collector_source),
                            "%depth%": sql.variable("%depth%", collector_source),
                            "%kind%": sql.string(kind),
                            "%label%": sql.string(target.identifier),
                            **{
                                variable.identifier: sql.variable(variable.identifier, collector_source)
                                for variable in output_variables[label]
                            },
                        })

                    case CFG.Return(variables):
                        contains_return = True
                        collector_column_expressions.update({
                            "%function%": sql.variable("%function%", collector_source),
                            "%caller%": sql.variable("%caller%", collector_source),
                            "%handle%": sql.variable("%handle%", collector_source),
                            "%depth%": sql.variable("%depth%", collector_source),
                            "%kind%": sql.string("return"),
                            **{
                                f"{function.name.identifier}%result#{i}": sql.cast(
                                    sql.variable(variable.identifier, collector_source),
                                    type.source
                                )
                                for i, (variable, type) in enumerate(zip(
                                    variables,
                                    function.return_types,
                                ))
                            }
                        })

                    case CFG.Call(handle, target, arguments):
                        calls_in_block.add(target)
                        collector_column_expressions.update({
                            "%function%": sql.string(target.identifier),
                            "%caller%": sql.variable("%function%", collector_source),
                            "%handle%": sql.string(handle.identifier),
                            "%depth%": f"{sql.variable("%depth%", collector_source)} + 1",
                            "%kind%": sql.string("call"),
                            "%label%": sql.string(target.identifier),
                            **{
                                parameter.identifier: sql.cast(
                                    sql.variable(argument.identifier, collector_source),
                                    type.source
                                )
                                for argument, (parameter, type) in zip(
                                    arguments,
                                    program.functions[target].parameters.items()
                                )
                            }
                        })

                block_collector_data.append((
                    collector_column_expressions,
                    predicates
                ))

            block_CTE_schema = {
                **dict(zip(
                    constant_control_columns,
                    constant_control_column_types,
                )),
                **dict(zip(
                    variable_control_columns,
                    variable_control_column_types,
                )),
                **{
                    variable.identifier: symbol_table[variable].source
                    for variable in sorted(
                        #? [note] Pull the functions arguments to the beginning
                        #? of the the state describing column. This is by no
                        #? means required its just a bit easier to debug, since
                        #? these variables/arguments are also pulled to the
                        #? start of the related columns in the top-level
                        #? recursive CTE.
                        input_variables[function.body.entry_label] &
                        output_variables[label]
                    )
                },
                **{
                    variable.identifier: symbol_table[variable].source
                    for variable in sorted(
                        #? [note] Skip any variables the may have already been
                        #? accounted for on account of them beeing parameters
                        #? of this function.
                        output_variables[label] -
                        input_variables[function.body.entry_label]
                    )
                },
            }

            if contains_return:
                block_CTE_schema |= {
                    f"{function.name.identifier}%result#{i}": type.source
                    for i, type in enumerate(function.return_types)
                }

            for called_function in sorted(calls_in_block):
                block_CTE_schema |= {
                    variable.identifier: type.source
                    for variable, type in program.functions[called_function].parameters.items()
                }

            calls_in_function.update(calls_in_block)

            block_collectors = [
                sql.select(
                    select_list=[
                        sql.named(
                            thing=(
                                expressions.get(
                                    column,
                                    sql.cast("NULL", type)
                                )
                            ),
                            name=column
                        )
                        for column, type in block_CTE_schema.items()
                    ],
                    from_list=[sql.name(collector_source)],
                    predicates=predicates
                )
                for expressions, predicates in block_collector_data
            ]

            block_CTEs.append(
                sql.cte(
                    name=label.identifier,
                    columns=list(block_CTE_schema.keys()),
                    body=sql.with_ctes(
                        ctes=step_ctes,
                        body=sql.union_all(block_collectors)
                    )
                )
            )

            function_collector_data.append(
                (
                    set(block_CTE_schema),
                    label.identifier
                )
            )

        function_CTE_name = function.name.identifier
        function_specfic_columns = {
            **{
                variable.identifier: symbol_table[variable].source
                for variable in sorted(
                    #? [note] Pull the functions arguments to the beginning
                    #? of the the state describing column. This is by no
                    #? means required its just a bit easier to debug, since
                    #? these variables/arguments are also pulled to the
                    #? start of the related columns in the top-level
                    #? recursive CTE.
                    input_variables[function.body.entry_label]
                )
            },
            **{
                variable.identifier: symbol_table[variable].source
                for variable in sorted(
                    #? [note] Skip any variables the may have already been
                    #? accounted for on account of them beeing parameters
                    #? of this function.
                    function_loop_carried_variables -
                    input_variables[function.body.entry_label]
                )
            },
            **{
                f"{function.name.identifier}%result#{i}": type.source
                for i, type in enumerate(function.return_types)
            }
        }
        function_CTE_schema = {
            **dict(zip(
                constant_control_columns,
                constant_control_column_types,
            )),
            **dict(zip(
                variable_control_columns,
                variable_control_column_types,
            )),
            **function_specfic_columns,
            **{
                variable.identifier: type.source
                for called_function in calls_in_function
                for variable, type in program.functions[called_function].parameters.items()
            }
        }

        function_collectors = [
            sql.select(
                select_list=[
                    sql.named(
                        thing=(
                            sql.variable(column, name)
                            if column in schema else
                            sql.cast("NULL", type)
                        ),
                        name=column
                    )
                    for column, type in function_CTE_schema.items()
                ],
                from_list=[sql.name(name)]
            )
            for schema, name in function_collector_data
        ]

        function_CTEs.append(
            sql.cte(
                name=function_CTE_name,
                columns=list(function_CTE_schema.keys()),
                body=sql.with_ctes(
                    ctes=block_CTEs,
                    body=sql.union_all(function_collectors)
                )
            )
        )

        program_collector_data.append(
            (
                function_CTE_name,
                set(function_CTE_schema),
                function_specfic_columns,
            )
        )

    program_CTE_schema = {
        **dict(zip(
            constant_control_columns,
            constant_control_column_types,
        )),
        **dict(zip(
            variable_control_columns,
            variable_control_column_types,
        )),
        **{
            column: type
            for _, _, function_specfic_columns in sorted(
                program_collector_data
            )
            for column, type in function_specfic_columns.items()
        }
    }

    program_collectors = [
        sql.select(
            select_list=[
                sql.named(
                    thing=(
                        sql.variable(column, name)
                        if column in schema else
                        sql.cast("NULL", type)
                    ),
                    name=column
                )
                for column, type in program_CTE_schema.items()
            ],
            from_list=[sql.name(name)]
        )
        for name, schema, _ in program_collector_data
    ]

    program_collectors.append(
        sql.select(
            select_list=[
                sql.variable(column, "%data%")
                for column in program_CTE_schema
            ],
            from_list=[sql.named(sql.name("%loop%"), "%data%")],
            predicates=[
                f"{sql.variable("%kind%", "%data%")} = "
                f"{sql.string("return")}"
            ],
            join_list=[
                sql.join(
                    table=sql.named(sql.name("%loop%"), "%wait%"),
                    predicates=[
                        f"{sql.variable("%kind%", "%wait%")} = "
                        f"{sql.string("wait")}",
                        f"{sql.variable("%function%", "%wait%")} = "
                        f"{sql.variable("%caller%", "%data%")}",
                        f"{sql.variable("%depth%", "%wait%")} = "
                        f"{sql.variable("%depth%", "%data%")} - 1",
                    ]
                )
            ],
        )
    )


    recursive_subquery = sql.with_ctes(
        ctes=function_CTEs,
        body=sql.union_all(program_collectors)
    )

    column_expressions = {
        "%function%": sql.string(program.main_function_name.identifier),
        "%depth%": "0",
        "%kind%": sql.string("call"),
        "%label%": sql.string(program.main_function_name.identifier),
    }

    if program.inputs is not None:
        from_list = [
            sql.named(
                sql.paren(program.inputs.source),
                name="%init%",
                columns=[
                    variable.identifier
                    for variable in program.main_function.parameters
                ]
            )
        ]
        column_expressions.update({
            argument.identifier: sql.variable(argument.identifier, "%init%")
            for argument in program.main_function.parameters
        })
    else:
        from_list = []

    nonrecursive_subquery = sql.select(
        select_list=[
            sql.named(
                thing=sql.cast(
                    column_expressions.get(column, "NULL"),
                    type
                ),
                name=column,
            )
            for column, type in program_CTE_schema.items()
        ],
        from_list=from_list
    )

    return sql.with_ctes(
        recursive=True,
        ctes=[
            sql.cte(
                name="%loop%",
                columns=list(program_CTE_schema),
                body=sql.union_all([
                    sql.paren(nonrecursive_subquery),
                    sql.paren(recursive_subquery)
                ])
            )
        ],
        body=sql.select(
            select_list=[
                sql.name(f"{program.main_function_name.identifier}%result#{i}")
                for i, _ in enumerate(program.main_function.return_types)
            ],
            from_list=[sql.name("%loop%")],
            predicates=[
                f"{sql.variable("%kind%")} = {sql.string('return')}",
                f"{sql.variable("%function%")} = {sql.string(program.main_function_name.identifier)}",
                f"{sql.variable("%depth%")} = 0",
                f"{sql.variable("%caller%")} IS NULL",
                f"{sql.variable("%handle%")} IS NULL"
            ]
        )
    ) + ";"


def gen_expression(expression: lowering.Expression, rowvar: str) -> str:
    try:
        return expression.source.format(*(
            f'({sql.variable(variable.identifier, rowvar)})'
            for variable in expression.arguments
        ))
    except Exception as e:
        raise CodeGenError(
            "Encountered an error during formatting of an "
            "embedded SQL expression.",
            expression.annotation,
            "",
            "Given Query:",
            expression.source,
            "",
            "Error:",
            repr(e)
        ) from e
