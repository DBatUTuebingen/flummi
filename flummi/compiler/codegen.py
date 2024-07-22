from dataclasses import dataclass
import itertools

from .analyzer import SymbolTable
from .data_flow import get_block_inputs
from ..IR import CFG, common
from ..library import sql, graph, utils


__all__ = (
    "codegen",
)



def codegen(program: CFG.Program, symbol_tables: dict[common.Identifier, SymbolTable]) -> str:
    return CodeGenerator().gen_program(program, symbol_tables)


class CodeGenError(Exception):
    ...


@dataclass
class CodeGenerator:
    def gen_program(self, program: CFG.Program, symbol_tables: dict[common.Identifier, SymbolTable]) -> sql.SQL:
        ctes: list[sql.SQL] = []
        collector_data: list[tuple[str, list[sql.SQL]]] = []

        init_list: list[sql.SQL] = [
            sql.named(
                sql.string(program.main_function_name.identifier),
                name=".function"
            ),
            sql.named(
                sql.string(program.main_function_name.identifier),
                name=".label"
            ),
            sql.named(
                sql.cast("0", type="INT"),
                name=".mark"
            )
        ]
        loop_column_prefix: list[sql.SQL] = []
        loop_schema: list[str] = [
            ".function",
            ".label",
            ".mark",
        ]

        for function in program.function_list:
            symbol_table = symbol_tables[function.name]
            successors = function.body.edges
            predecessors = graph.invert(successors)
            inputs, loop_caried_variables = get_block_inputs(function.body)
            loop_caried_variables = list(sorted(loop_caried_variables))
            outputs = {
                label: sorted(utils.union(
                    inputs[successor]
                    for successor in successors[label]
                ))
                for label in inputs
            }

            sink_names: list[str] = []
            emit_names: list[str] = []

            for label in graph.dependent_ordering(successors):
                cte_name = f"{function.name.identifier}.{label.identifier}"
                these_successors = successors[label]
                these_predecessors = predecessors[label]

                node = function.body.nodes[label]
                match node:
                    case CFG.Source(name):
                        assert len(these_predecessors) == 0
                        #! [warn] This a hack to dodge nodes that where unnessarily generated.
                        if len(these_successors) == 0:
                            continue

                        columns = [
                            variable.identifier
                            for variable in outputs[label]
                        ]

                        ctes.append(
                            sql.cte(
                                name=cte_name,
                                columns=[
                                    ".mark",
                                ] + columns,
                                body=sql.select(
                                    select_list=[
                                        sql.variable(row="input", column=".mark"),
                                    ] + [
                                        sql.variable(
                                            row="input",
                                            column=f"{function.name.identifier}.{column}"
                                        )
                                        for column in columns
                                    ],
                                    from_list=[
                                        sql.named(
                                            sql.name("loop"),
                                            name="input"
                                        )
                                    ],
                                    predicates=[
                                        sql.variable(row="input", column=".function") + " = " +
                                        sql.string(function.name.identifier),
                                        sql.variable(row="input", column=".label") + " = " +
                                        sql.string(name.identifier),
                                    ]
                                )
                            )
                        )

                    case CFG.Sink(name):
                        assert len(these_predecessors) == 1
                        assert len(these_successors) == 0
                        predecessor = these_predecessors.pop()

                        columns = [
                            variable.identifier
                            for variable in loop_caried_variables
                        ]

                        ctes.append(
                            sql.cte(
                                name=cte_name,
                                columns=[
                                    ".label",
                                    ".mark",
                                ] + columns,
                                body=sql.select(
                                    select_list=[
                                        sql.named(
                                            sql.string(name.identifier),
                                            name=".label"
                                        ),
                                        sql.variable(row="input", column=".mark"),
                                    ] + [
                                        sql.variable(row="input", column=column)
                                        for column in columns
                                    ],
                                    from_list=[
                                        sql.named(
                                            sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                            name="input"
                                        )
                                    ]
                                )
                            )
                        )
                        sink_names.append(cte_name)

                    case CFG.Conditional(truthy, falsey):
                        assert len(these_predecessors) == 1
                        #! [warn] This a hack to dodge nodes that where unnessarily generated.
                        if len(these_successors) == 0:
                            continue
                        predecessor = these_predecessors.pop()

                        columns = [
                            variable.identifier
                            for variable in outputs[label]
                        ]

                        ctes.append(
                            sql.cte(
                                name=cte_name,
                                columns=[
                                    ".mark",
                                ] + columns,
                                body=sql.select(
                                    select_list=[
                                        sql.variable(row="input", column=".mark"),
                                    ] + [
                                        sql.variable(row="input", column=column)
                                        for column in columns
                                    ],
                                    from_list=[
                                        sql.named(
                                            sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                            name="input",
                                        )
                                    ],
                                    predicates=[
                                        *(
                                            sql.variable(row="input", column=variable.identifier)
                                            for variable in truthy
                                        ),
                                        *(
                                            "NOT " + sql.variable(row="input", column=variable.identifier)
                                            for variable in falsey
                                        ),
                                    ]
                                )
                            )
                        )

                    case CFG.Merge():
                        if len(these_successors) == 0:
                            continue
                        columns = [
                            variable.identifier
                            for variable in outputs[label]
                        ]
                        ctes.append(
                            sql.cte(
                                name=cte_name,
                                columns=[
                                    ".mark",
                                ] + columns,
                                body=sql.union_all([
                                    sql.select(
                                        select_list=[
                                            sql.variable(row="input", column=".mark"),
                                        ] + [
                                            sql.variable(row="input", column=column)
                                            for column in columns
                                        ],
                                        from_list=[
                                            sql.named(
                                                sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                                name="input",
                                            )
                                        ]
                                    )
                                    for predecessor in these_predecessors
                                ])
                            )
                        )

                    case CFG.Emits(emits):
                        assert len(these_predecessors) == 1
                        assert len(these_successors) == 0
                        predecessor = these_predecessors.pop()

                        subqueries = [
                            sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".mark"),
                                ] + [
                                    sql.cast(
                                        sql.variable(row="input", column=variable.identifier),
                                        type.source
                                    )
                                    for variable, type in zip(emit.variables, function.return_types)
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                        name="input",
                                    )
                                ]
                            )
                            for emit in emits
                        ]

                        ctes.append(
                            sql.cte(
                                name=cte_name,
                                columns=[
                                    ".mark",
                                ] + [
                                    f".result.{i}"
                                    for i in range(len(function.return_types))
                                ],
                                body=sql.union_all(subqueries)
                            )
                        )

                        emit_names.append(cte_name)

                    case CFG.Assignments(assignments):
                        assert len(these_predecessors) == 1
                        #! [warn] This a hack to dodge nodes that where unnessarily generated.
                        if len(these_successors) == 0:
                            continue
                        predecessor = these_predecessors.pop()

                        scalar_assignments, multi_assignments =\
                            utils.partition(
                                assignments,
                                choice=lambda assignment: len(assignment.variables) == 1
                            )

                        column_expressions = {
                            assignment.variables[0]: sql.named(
                                sql.cast(
                                    assignment.expression.source.format(*(
                                        sql.variable(row="input", column=variable.identifier)
                                        for variable in assignment.expression.arguments
                                    )),
                                    symbol_table[assignment.variables[0]].source
                                ),
                                name=f"{assignment.variables[0].identifier}"
                            )

                            for assignment in scalar_assignments
                        }

                        from_list = [
                            sql.named(
                                sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                name="input",
                            )
                        ]

                        for i, assignment in enumerate(multi_assignments):
                            row_variable = f"assignment.{i}"
                            column_expressions.update({
                                variable: sql.cast(
                                    sql.variable(row=row_variable, column=variable.identifier),
                                    symbol_table[variable].source
                                )
                                for variable in assignment.variables
                            })
                            from_list.append(
                                sql.named(
                                    sql.lateral(
                                        assignment.expression.source.format(*(
                                            sql.variable(row="input", column=variable.identifier)
                                            for variable in assignment.expression.arguments
                                        ))
                                    ),
                                    name=row_variable,
                                    columns=[
                                        variable.identifier
                                        for variable in assignment.variables
                                    ]
                                )
                            )

                        ctes.append(
                            sql.cte(
                                name=cte_name,
                                columns=[
                                    ".mark",
                                ] + [
                                    variable.identifier
                                    for variable in outputs[label]
                                ],
                                body=sql.select(
                                    select_list=[
                                        sql.variable(row="input", column=".mark"),
                                    ] + [
                                        column_expressions.get(
                                            variable,
                                            sql.variable(row="input", column=variable.identifier)
                                        )
                                        for variable in outputs[label]
                                    ],
                                    from_list=from_list
                                )
                            )
                        )

                    case CFG.Fork(variables, expression):
                        ctes.append(
                            sql.cte(
                                name=cte_name,
                                columns=[
                                    ".mark"
                                ] + [
                                    variable.identifier
                                    for variable in outputs[label]
                                ],
                                body=sql.select(
                                    select_list=[
                                        sql.variable(row="input", column=".mark"),
                                    ] + [
                                        sql.cast(
                                            sql.variable(
                                                row="fork",
                                                column=sql.name(variable.identifier),
                                            ),
                                            type=symbol_table[variable].source
                                        )
                                        if variable in variables else
                                        sql.variable(
                                            row="input",
                                            column=sql.name(f"{function.name.identifier}.{variable.identifier}"),
                                        )
                                        for variable in outputs[label]
                                    ],
                                    from_list=[
                                        sql.named(
                                            sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                            name="input",
                                        ),
                                        sql.named(
                                            sql.lateral(
                                                expression.source.format(*(
                                                    sql.variable(row="input", column=variable.identifier)
                                                    for variable in assignment.expression.arguments
                                                ))
                                            ),
                                            name="fork",
                                            columns=[
                                                variable.identifier
                                                for variable in variables
                                            ]
                                        )
                                    ]
                                )
                            )
                        )

                    case CFG.Aggregate(aggregates):
                        ctes.append(
                            sql.cte(
                                name=cte_name,
                                columns=[
                                    ".mark"
                                ] + [
                                    variable.identifier
                                    for variable in outputs[label]
                                ],
                                body=sql.select(
                                    select_list=[
                                        f"MIN({sql.variable(row="input", column=".mark")})"
                                    ] + [
                                        sql.named(
                                            expression.source.format(*(
                                                f"{function.name.identifier}.{argument.identifier}"
                                                for argument in expression.arguments
                                            )),
                                            name=variable.identifier
                                        )
                                        if (expression := aggregates.get(variable)) is not None else
                                        sql.variable(
                                            row="input",
                                            column=f"{function.name.identifier}.{variable.identifier}"
                                        )
                                        for variable in outputs[label]
                                    ],
                                    from_list=[
                                        sql.named(
                                            sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                            name="input",
                                        ),
                                    ],
                                    group_keys=[
                                        variable.identifier
                                        for variable in outputs[label]
                                        if variable not in aggregates
                                    ]
                                )
                            )
                        )

                    case CFG.Mark():
                        ctes.append(
                            sql.cte(
                                name=cte_name,
                                columns=[
                                    ".mark",
                                ] + [
                                    variable.identifier
                                    for variable in outputs[label]
                                ],
                                body=sql.select(
                                    select_list=[
                                        sql.named(
                                            sql.variable(row="input", column=".mark") + " + 1",
                                            name=".mark"
                                        )
                                    ] + [
                                        sql.variable(
                                            row="input",
                                            column=f"{function.name.identifier}.{variable.identifier}"
                                        )
                                        for variable in outputs
                                    ],
                                    from_list=[
                                        sql.named(
                                            sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                            name="input",
                                        ),
                                    ]
                                )
                            ),
                        )

                    case CFG.Wait():
                        gather_cte_name = cte_name + ".gather"
                        ctes.append(
                            sql.cte(
                                name=gather_cte_name,
                                columns=[
                                    ".mark",
                                    ".done",
                                ] + [
                                    variable.identifier
                                    for variable in outputs[label]
                                ],
                                body=sql.union_all([
                                    sql.select(
                                        select_list=[
                                            sql.named(
                                                sql.variable(row="input", column=".mark") + " - 1",
                                                name=".mark"
                                            ),
                                            sql.named(
                                                sql.prefix_token(
                                                    prefix="NOT",
                                                    content=sql.call(
                                                        function="EXISTS",
                                                        arguments=[sql.select(
                                                            select_list=[sql.named("1", name="dummy")],
                                                            from_list=[sql.name("loop")],
                                                            predicates=[
                                                                sql.variable(row="loop", column=".function") + " = " +
                                                                sql.string(function.name.identifier),
                                                                sql.variable(row="loop", column=".mark") + " >= " +
                                                                sql.variable(row="input", column=".mark"),
                                                            ]
                                                        )]
                                                    )
                                                ),
                                                name=".done"
                                            )
                                        ] + [
                                            sql.variable(
                                                row="input",
                                                column=f"{function.name.identifier}.{variable.identifier}"
                                            )
                                            for variable in outputs
                                        ],
                                        from_list=[
                                            sql.named(
                                                sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                                name="input",
                                            ),
                                        ],
                                    ),
                                    sql.select(
                                        select_list=[
                                            sql.variable(row="input", column=".mark"),
                                            sql.named("true", name=".done")
                                        ] + [
                                            sql.variable(
                                                row="input",
                                                column=f"{function.name.identifier}.{variable.identifier}"
                                            )
                                            for variable in outputs
                                        ],
                                        from_list=[
                                            sql.named(
                                                sql.name("loop"),
                                                name="input",
                                            ),
                                        ],
                                        predicates=[
                                            sql.variable(row="input", column=".function") + " = " +
                                            sql.string(function.name.identifier),
                                            sql.variable(row="input", column=".label") + " = " +
                                            sql.string(label.identifier),
                                        ]
                                    ),
                                ])
                            )
                        )
                        decide_cte_name = cte_name + ".decide"
                        ctes.append(
                            sql.cte(
                                name=decide_cte_name,
                                columns=[
                                    ".mark",
                                    ".all done",
                                ] + [
                                    variable.identifier
                                    for variable in outputs[label]
                                ],
                                body=sql.select(
                                    select_list=[
                                            sql.variable(row="input", column=".mark"),
                                            sql.named(
                                                sql.window(
                                                    sql.call(
                                                        function="BOOL_AND",
                                                        arguments=[
                                                            sql.variable(row="input", column=".done")
                                                        ]
                                                    ),
                                                    partition_by=[
                                                        sql.variable(row="input", column=".mark"),
                                                    ],
                                                    rows=(
                                                        "UNBOUNDED PRECEDING",
                                                        "UNBOUNDED FOLLOWING",
                                                    )
                                                ),
                                                name=".all done"
                                            )
                                        ] + [
                                            sql.variable(
                                                row="input",
                                                column=f"{function.name.identifier}.{variable.identifier}"
                                            )
                                            for variable in outputs
                                        ],
                                    from_list=[
                                        sql.named(
                                            gather_cte_name,
                                            name="input"
                                        )
                                    ]
                                )
                            )
                        )
                        wait_cte_name = cte_name + ".wait"
                        ctes.append(
                            sql.cte(
                                name=wait_cte_name,
                                columns=[
                                    ".mark",
                                    ".label",
                                ] + [
                                    variable.identifier
                                    for variable in outputs[label]
                                ],
                                body=sql.select(
                                    select_list=[
                                            sql.variable(row="input", column=".mark"),
                                            sql.named(
                                                sql.string(label.identifier),
                                                name=".label"
                                            )
                                        ] + [
                                            sql.variable(
                                                row="input",
                                                column=f"{function.name.identifier}.{variable.identifier}"
                                            )
                                            for variable in outputs
                                        ],
                                    from_list=[
                                        sql.named(
                                            sql.name(wait_cte_name),
                                            name="input"
                                        )
                                    ],
                                    predicates=[
                                        "NOT + " + sql.variable(row="input", column=".all done")
                                    ]
                                )
                            )
                        )
                        sink_names.append(wait_cte_name)
                        ctes.append(
                            sql.cte(
                                name=cte_name,
                                columns=[
                                    ".mark",
                                ] + [
                                    variable.identifier
                                    for variable in outputs[label]
                                ],
                                body=sql.select(
                                    select_list=[
                                            sql.variable(row="input", column=".mark")
                                        ] + [
                                            sql.variable(
                                                row="input",
                                                column=f"{function.name.identifier}.{variable.identifier}"
                                            )
                                            for variable in outputs
                                        ],
                                    from_list=[
                                        sql.named(
                                            sql.name(wait_cte_name),
                                            name="input"
                                        )
                                    ],
                                    predicates=[
                                        sql.variable(row="input", column=".all done")
                                    ]
                                )
                            )
                        )

            schema = [
                *(
                    (
                        f"{function.name.identifier}.{variable.identifier}",
                        symbol_table[variable]
                    )
                    for variable in loop_caried_variables
                ),
                *(
                    (
                        f"{function.name.identifier}.result.{i}",
                        type
                    )
                    for i, type in enumerate(function.return_types)
                )
            ]

            loop_schema.extend(
                column
                for column, _ in schema
            )

            nulls = [
                sql.named(
                    sql.cast(
                        "NULL",
                        type.source
                    ),
                    name=column
                )
                for column, type in schema
            ]

            if function.name == program.main_function_name:
                init_list.extend(
                    sql.named(
                        sql.cast(
                            sql.variable(
                                row="input",
                                column=variable.identifier
                            )
                            if variable in function.parameters else
                            "NULL",
                            symbol_table[variable].source
                        ),
                        name=f"{function.name.identifier}.{variable.identifier}",
                    )
                    for variable in loop_caried_variables
                )
                init_list.extend(
                    sql.named(
                        sql.cast(
                            "NULL",
                            type.source
                        ),
                        name=f"{function.name.identifier}.result.{i}",
                    )
                    for i, type in enumerate(function.return_types)
                )
            else:
                init_list.extend(nulls)

            collector_data = [
                (
                    name,
                    columns + nulls
                )
                for name, columns in collector_data
            ]
            collector_data.extend(
                (
                    name,
                    [
                        sql.named(
                            sql.string(function.name.identifier),
                            name=".function"
                        ),
                        sql.variable(".label"),
                        sql.variable(".mark"),
                    ] +
                    loop_column_prefix +
                    [
                        *(
                            sql.variable(variable.identifier)
                            for variable in loop_caried_variables
                        ),
                        *(
                            sql.named(
                                sql.cast(
                                    "NULL",
                                    type.source
                                ),
                                name=f"{function.name.identifier}.result.{i}"
                            )
                            for i, type in enumerate(function.return_types)
                        )
                    ]
                )
                for name in sink_names
            )
            collector_data.extend(
                (
                    name,
                    [
                        sql.named(
                            sql.string(function.name.identifier),
                            name=".function"
                        ),
                        sql.named(
                            sql.cast(
                                "NULL",
                                "TEXT"
                            ),
                            name=".label"
                        ),
                        sql.variable(".mark"),
                    ] +
                    loop_column_prefix +
                    [
                        *(
                            sql.named(
                                sql.cast(
                                    "NULL",
                                    symbol_table[variable].source
                                ),
                                name=f"{function.name.identifier}.{variable.identifier}"
                            )
                            for variable in loop_caried_variables
                        ),
                        *(
                            sql.variable(f".result.{i}")
                            for i in range(len(function.return_types))
                        )
                    ]
                )
                for name in emit_names
            )
            loop_column_prefix += nulls


        initial_call = sql.select(
            select_list=init_list,
            from_list=[
                sql.named(
                    sql.paren(program.inputs.source),
                    name="input",
                    columns=[
                        parameter.identifier
                        for parameter in program.main_function.parameters
                    ]
                )
            ] if program.inputs else []
        )

        return sql.with_ctes(
            [sql.cte(
                name="loop",
                columns=loop_schema,
                body=sql.union_all([
                    initial_call,
                    sql.with_ctes(
                        ctes,
                        body=sql.union_all([
                            sql.select(
                                select_list=columns,
                                from_list=[sql.name(name)]
                            )
                            for name, columns in collector_data
                        ])
                    )
                ])
            )],
            recursive=True,
            body=sql.select(
                select_list=[
                    sql.variable(
                        row="loop",
                        column=f"{program.main_function_name.identifier}.result.{i}"
                    )
                    for i in range(len(program.main_function.return_types))
                ],
                from_list=[sql.name("loop")],
                predicates=[
                    sql.variable(row="loop", column=".label") + " IS NULL",
                    sql.variable(row="loop", column=".function") + " = " +
                    sql.string(program.main_function_name.identifier)
                ]
            )
        )
