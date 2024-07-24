from dataclasses import dataclass
import itertools

from .analyzer import SymbolTable
from .data_flow import get_block_inputs, get_block_outputs
from ..IR import CFG, common
from ..library import sql, graph, utils


__all__ = (
    "codegen",
)



def codegen(
    program: CFG.Program,
    symbol_tables: dict[common.Identifier, SymbolTable],
    explicit_materialized: bool = False,
    avoid_multiple_recursive_references: bool = False,
) -> str:
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
        inputs = get_block_inputs(function.body)
        outputs = {
            label: list(sorted(variables))
            for label, variables in get_block_outputs(function.body, inputs).items()
        }

        loop_carried_variables = list(sorted(utils.union(
            outputs[label]
            for label, node in function.body.nodes.items()
            if isinstance(node, (CFG.Source, CFG.Wait))
        )))

        emits: list[str] = []
        sinks: list[tuple[str, set[common.Identifier]]] = []

        for label in graph.dependent_ordering(successors):
            cte_name = f"{function.name.identifier}.{label.identifier}"
            these_successors = successors[label]
            these_predecessors = predecessors[label]

            node = function.body.nodes[label]
            match node:
                case CFG.Source(name):
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
                    assert len(these_successors) == 0
                    assert len(these_predecessors) == 1
                    predecessor = these_predecessors.pop()

                    columns = [
                        variable.identifier
                        for variable in outputs[label]
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
                    sinks.append((
                        cte_name,
                        set(outputs[label])
                    ))

                case CFG.Conditional(truthy, falsey):
                    assert len(these_predecessors) == 1
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
                            materialize=explicit_materialized and len(these_successors) > 1,
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

                case CFG.Emit(variables):
                    assert len(these_predecessors) == 1
                    assert len(these_successors) == 0
                    predecessor = these_predecessors.pop()

                    ctes.append(
                        sql.cte(
                            name=cte_name,
                            columns=[
                                ".mark",
                            ] + [
                                f".result.{i}"
                                for i in range(len(function.return_types))
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".mark"),
                                ] + [
                                    sql.cast(
                                        sql.variable(row="input", column=variable.identifier),
                                        type.source
                                    )
                                    for variable, type in zip(variables, function.return_types)
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                        name="input",
                                    )
                                ]
                            )
                        )
                    )

                    emits.append(cte_name)

                case CFG.Assignment([variable], expression):
                    assert len(these_predecessors) == 1
                    predecessor = these_predecessors.pop()

                    ctes.append(
                        sql.cte(
                            name=cte_name,
                            materialize=explicit_materialized and len(these_successors) > 1,
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
                                    expression.source.format(*(
                                        sql.variable(row="input", column=variable.identifier)
                                        for variable in expression.arguments
                                    ))
                                    if output == variable else
                                    sql.variable(row="input", column=variable.identifier)
                                    for output in outputs[label]
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                        name="input",
                                    )
                                ]
                            )
                        )
                    )

                case CFG.Assignment(variables, expression):
                    assert len(these_predecessors) == 1
                    predecessor = these_predecessors.pop()

                    ctes.append(
                        sql.cte(
                            name=cte_name,
                            materialize=explicit_materialized and len(these_successors) > 1,
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
                                    sql.variable(
                                        row="assign" if output in variables else "input",
                                        column=variable.identifier
                                    )
                                    for output in outputs[label]
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
                                                for variable in expression.arguments
                                            ))
                                        ),
                                        name="assign",
                                        columns=[
                                            variable.identifier
                                            for variable in variables
                                        ]
                                    )
                                ]
                            )
                        )
                    )

                case CFG.Fork(variables, expression):
                    assert len(these_predecessors) == 1
                    predecessor = these_predecessors.pop()

                    ctes.append(
                        sql.cte(
                            name=cte_name,
                            materialize=explicit_materialized and len(these_successors) > 1,
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
                                            column=variable.identifier,
                                        ),
                                        type=symbol_table[variable].source
                                    )
                                    if variable in variables else
                                    sql.variable(row="input", column=variable.identifier)
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
                                                for variable in expression.arguments
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

                case CFG.Join(variables, expression):
                    assert len(these_predecessors) == 1
                    predecessor = these_predecessors.pop()

                    group_keys = [
                        variable
                        for variable in outputs[label]
                        if variable not in variables
                    ]

                    group_key_query = sql.named(
                        sql.paren(
                            sql.select(
                                select_list=[
                                    sql.named(
                                        sql.call(
                                            function="MIN",
                                            arguments=[sql.variable(row="key", column=".mark")]
                                        ),
                                        name=".mark"
                                    )
                                ] + [
                                    sql.variable(row="key", column=variable.identifier)
                                    for variable in group_keys
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                        name="key"
                                    )
                                ],
                                group_keys=[
                                    sql.variable(row="key", column=variable.identifier)
                                    for variable in group_keys
                                ],
                            )
                        ),
                        name="key",
                        columns=[".mark"] + [
                            variable.identifier
                            for variable in group_keys
                        ]
                    )

                    aggregate_query = sql.named(
                        sql.lateral(
                            expression.source.format(*(
                                sql.variable(row="input", column=argument.identifier)
                                for argument in expression.arguments
                            )).format(
                                sql.named(
                                    sql.paren(
                                        sql.select(
                                            select_list=[
                                                sql.variable(row="input", column=argument.identifier)
                                                for argument in expression.arguments
                                            ],
                                            from_list=[
                                                sql.named(
                                                    sql.name(f"{function.name.identifier}.{predecessor.identifier}"),
                                                    name="input"
                                                )
                                            ],
                                            predicates=[
                                                sql.variable(row="key", column=variable.identifier)  + " = " +
                                                sql.variable(row="input", column=variable.identifier)
                                                for variable in group_keys
                                            ]
                                        )
                                    ),
                                    name="input"
                                )
                            )
                        ),
                        name="aggregate",
                        columns=[
                            variable.identifier
                            for variable in variables
                        ]
                    )

                    ctes.append(
                        sql.cte(
                            name=cte_name,
                            materialize=explicit_materialized and len(these_successors) > 1,
                            columns=[
                                ".mark"
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="key", column=".mark")
                                ] + [
                                    sql.cast(
                                        sql.variable(
                                            row="aggregate",
                                            column=variable.identifier
                                        ),
                                        type=symbol_table[variable].source
                                    )
                                    if variable in variables else
                                    sql.variable(
                                        row="key",
                                        column=variable.identifier
                                    )
                                    for variable in outputs[label]
                                ],
                                from_list=[
                                    group_key_query,
                                    aggregate_query,
                                ],
                                predicates=[
                                    sql.variable(row="key", column=".mark") + " IS NOT NULL"
                                ]
                            )
                        )
                    )

                case CFG.Mark():
                    assert len(these_predecessors) == 1
                    predecessor = these_predecessors.pop()

                    snapshot_cte_name = cte_name + ".snapshot"
                    ctes.append(
                        sql.cte(
                            name=snapshot_cte_name,
                            columns=[
                                ".label",
                                ".mark",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.named(
                                        sql.string(label.identifier),
                                        name=".label"
                                    ),
                                    sql.named(
                                        sql.variable(row="input", column=".mark") + " + 1",
                                        name=".mark"
                                    )
                                ] + [
                                    sql.variable(row="input", column=variable.identifier)
                                    for variable in outputs[label]
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
                    sinks.append((
                        snapshot_cte_name,
                        set(outputs[label])
                    ))

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
                                    sql.variable(
                                        row="input",
                                        column=f"{function.name.identifier}.{variable.identifier}"
                                    )
                                    for variable in outputs[label]
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
                                    sql.string(label.identifier),
                                ]
                            )
                        )
                    )

                case CFG.Wait():
                    assert len(these_predecessors) == 1
                    predecessor = these_predecessors.pop()

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
                                        sql.variable(row="input", column=variable.identifier)
                                        for variable in outputs[label]
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
                                        for variable in outputs[label]
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
                            materialize=explicit_materialized,
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
                                        sql.variable(row="input", column=variable.identifier)
                                        for variable in outputs[label]
                                    ],
                                from_list=[
                                    sql.named(
                                        sql.name(gather_cte_name),
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
                                        sql.variable(row="input", column=variable.identifier)
                                        for variable in outputs[label]
                                    ],
                                from_list=[
                                    sql.named(
                                        sql.name(decide_cte_name),
                                        name="input"
                                    )
                                ],
                                predicates=[
                                    "NOT " + sql.variable(row="input", column=".all done")
                                ]
                            )
                        )
                    )
                    sinks.append((
                        wait_cte_name,
                        set(outputs[label])
                    ))
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
                                        sql.variable(row="input", column=variable.identifier)
                                        for variable in outputs[label]
                                    ],
                                from_list=[
                                    sql.named(
                                        sql.name(decide_cte_name),
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
                for variable in loop_carried_variables
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
                for variable in loop_carried_variables
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
                sql.name(name),
                columns + nulls
            )
            for name, columns in collector_data
        ]
        collector_data.extend(
            (
                sql.named(sql.name(name), name="sink"),
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
                        sql.named(
                            sql.variable(row="sink", column=variable.identifier),
                            name=f"{function.name.identifier}.{variable.identifier}"
                        )
                        if variable in variables else
                        sql.named(
                            sql.cast(
                                "NULL",
                                symbol_table[variable].source
                            ),
                            name=f"{function.name.identifier}.{variable.identifier}"
                        )
                        for variable in loop_carried_variables
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
            for name, variables in sinks
        )
        collector_data.extend(
            (
                sql.named(sql.name(name), name="emit"),
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
                        for variable in loop_carried_variables
                    ),
                    *(
                        sql.variable(row="emit", column=f".result.{i}")
                        for i in range(len(function.return_types))
                    )
                ]
            )
            for name in emits
        )
        loop_column_prefix += nulls

    if avoid_multiple_recursive_references:
        ctes = [
            sql.cte(
                name="loop",
                columns=loop_schema,
                body=sql.select(
                    select_list=["*"],
                    from_list=[sql.name("loop")],
                )
            )
        ] + ctes

    whole_program = sql.with_ctes(
        ctes=[sql.cte(
            name="loop",
            columns=loop_schema,
            body=sql.union_all([
                sql.select(
                    select_list=init_list
                ),
                sql.with_ctes(
                    ctes,
                    body=sql.union_all([
                        sql.select(
                            select_list=columns,
                            from_list=[relation]
                        )
                        for relation, columns in collector_data
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

    if program.inputs:
        return sql.select(
            select_list=['"input".*', '"result".*'],
            from_list=[
                sql.named(
                    sql.paren(program.inputs.source),
                    name="input",
                    columns=[
                        parameter.identifier
                        for parameter in program.main_function.parameters
                    ]
                ),
                sql.named(
                    sql.lateral(whole_program),
                    name="result"
                )
            ]
        )
    else:
        return whole_program
