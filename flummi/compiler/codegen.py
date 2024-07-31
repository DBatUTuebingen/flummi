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
            sql.cast("0", type="INT"),
            name=".iteration"
        ),
        sql.named(
            sql.cast("0", type="INT"),
            name=".mark"
        ),
        sql.named(
            sql.cast("0", type="INT"),
            name=".thread.this"
        ),
        sql.named(
            sql.string(program.main_function_name.identifier),
            name=".label.this"
        ),
        sql.named(
            sql.cast(sql.NULL, type="INT"),
            name=".thread.parent"
        ),
        sql.named(
            sql.cast(sql.NULL, type="TEXT"),
            name=".label.parent"
        ),
    ]
    loop_column_prefix: list[sql.SQL] = []
    loop_schema: list[str] = [
        ".iteration",
        ".mark",
        ".thread.this",
        ".label.this",
        ".thread.parent",
        ".label.parent",
    ]

    calls: list[tuple[str, common.Identifier]] = []

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
            if isinstance(node, (CFG.Source, CFG.Wait, CFG.Call, CFG.Mark))
        )))

        emits: list[str] = []
        sinks: list[tuple[str, set[common.Identifier]]] = []

        for label in graph.dependent_ordering(successors):
            cte_name = label.identifier
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + columns,
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.variable(row="input", column=".mark"),
                                    sql.variable(row="input", column=".thread.this"),
                                    sql.variable(row="input", column=".thread.parent"),
                                    sql.variable(row="input", column=".label.parent"),
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
                                    sql.variable(row="input", column=".label.this") + " IS NOT DISTINCT FROM " +
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".label.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + columns,
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.variable(row="input", column=".mark"),
                                    sql.variable(row="input", column=".thread.this"),
                                    sql.named(
                                        sql.string(name.identifier),
                                        name=".label.this"
                                    ),
                                    sql.variable(row="input", column=".thread.parent"),
                                    sql.variable(row="input", column=".label.parent"),
                                ] + [
                                    sql.variable(row="input", column=column)
                                    for column in columns
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(predecessor.identifier),
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + columns,
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.variable(row="input", column=".mark"),
                                    sql.variable(row="input", column=".thread.this"),
                                    sql.variable(row="input", column=".thread.parent"),
                                    sql.variable(row="input", column=".label.parent"),
                                ] + [
                                    sql.variable(row="input", column=column)
                                    for column in columns
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(predecessor.identifier),
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + columns,
                            body=sql.union_all([
                                sql.select(
                                    select_list=[
                                        sql.variable(row="input", column=".iteration"),
                                        sql.variable(row="input", column=".mark"),
                                        sql.variable(row="input", column=".thread.this"),
                                        sql.variable(row="input", column=".thread.parent"),
                                        sql.variable(row="input", column=".label.parent"),
                                    ] + [
                                        sql.variable(row="input", column=column)
                                        for column in columns
                                    ],
                                    from_list=[
                                        sql.named(
                                            sql.name(predecessor.identifier),
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                f".result.{i}"
                                for i in range(len(function.return_types))
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.variable(row="input", column=".mark"),
                                    sql.variable(row="input", column=".thread.this"),
                                    sql.variable(row="input", column=".thread.parent"),
                                    sql.variable(row="input", column=".label.parent"),
                                ] + [
                                    sql.cast(
                                        sql.variable(row="input", column=variable.identifier),
                                        type.source
                                    )
                                    for variable, type in zip(variables, function.return_types)
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(predecessor.identifier),
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.variable(row="input", column=".mark"),
                                    sql.variable(row="input", column=".thread.this"),
                                    sql.variable(row="input", column=".thread.parent"),
                                    sql.variable(row="input", column=".label.parent"),
                                ] + [
                                    sql.named(
                                        sql.cast(
                                            expression.source.format(*(
                                                sql.variable(row="input", column=variable.identifier)
                                                for variable in expression.arguments
                                            )),
                                            type=symbol_table[output].source
                                        ),
                                        name=output.identifier
                                    )
                                    if output == variable else
                                    sql.variable(row="input", column=output.identifier)
                                    for output in outputs[label]
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(predecessor.identifier),
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.variable(row="input", column=".mark"),
                                    sql.variable(row="input", column=".thread.this"),
                                    sql.variable(row="input", column=".thread.parent"),
                                    sql.variable(row="input", column=".label.parent"),
                                ] + [
                                    sql.variable(
                                        row="assign" if output in variables else "input",
                                        column=variable.identifier
                                    )
                                    for output in outputs[label]
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(predecessor.identifier),
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.variable(row="input", column=".mark"),
                                    sql.variable(row="input", column=".thread.this"),
                                    sql.variable(row="input", column=".thread.parent"),
                                    sql.variable(row="input", column=".label.parent"),
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
                                        sql.name(predecessor.identifier),
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
                        ".iteration",
                        ".thread.this",
                        ".thread.parent",
                        ".label.parent",
                    ] + [
                        variable.identifier
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
                                    ),
                                ] + [
                                    sql.variable(row="key", column=variable)
                                    for variable in group_keys
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(predecessor.identifier),
                                        name="key"
                                    )
                                ],
                                group_keys=[
                                    sql.variable(row="key", column=variable)
                                    for variable in group_keys
                                ],
                            )
                        ),
                        name="key",
                        columns=[
                            ".mark",
                        ] + [
                            variable
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
                                                sql.cast(
                                                    sql.variable(row="input", column=argument.identifier),
                                                    type=symbol_table[argument].source
                                                )
                                                for argument in expression.arguments
                                            ],
                                            from_list=[
                                                sql.named(
                                                    sql.name(predecessor.identifier),
                                                    name="input"
                                                )
                                            ],
                                            predicates=[
                                                sql.variable(row="key", column=variable)  + " IS NOT DISTINCT FROM " +
                                                sql.variable(row="input", column=variable)
                                                for variable in group_keys
                                            ]
                                        )
                                    ),
                                    name="input",
                                    columns=[
                                        argument.identifier
                                        for argument in expression.arguments
                                    ]
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="key", column=".iteration"),
                                    sql.variable(row="key", column=".mark"),
                                    sql.variable(row="key", column=".thread.this"),
                                    sql.variable(row="key", column=".thread.parent"),
                                    sql.variable(row="key", column=".label.parent"),
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".label.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.named(
                                        sql.variable(row="input", column=".mark") + " + 1",
                                        name=".mark"
                                    ),
                                    sql.variable(row="input", column=".thread.this"),
                                    sql.named(
                                        sql.string(label.identifier),
                                        name=".label.this"
                                    ),
                                    sql.variable(row="input", column=".thread.parent"),
                                    sql.variable(row="input", column=".label.parent"),
                                ] + [
                                    sql.variable(row="input", column=variable.identifier)
                                    for variable in outputs[label]
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(predecessor.identifier),
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.variable(row="input", column=".mark"),
                                    sql.variable(row="input", column=".thread.this"),
                                    sql.variable(row="input", column=".thread.parent"),
                                    sql.variable(row="input", column=".label.parent"),
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
                                    sql.variable(row="input", column=".label.this") + " IS NOT DISTINCT FROM " +
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.union_all([
                                sql.select(
                                    select_list=[
                                        sql.variable(row="input", column=".iteration"),
                                        sql.named(
                                            sql.variable(row="input", column=".mark") + " - 1",
                                            name=".mark"
                                        ),
                                        sql.variable(row="input", column=".thread.this"),
                                        sql.variable(row="input", column=".thread.parent"),
                                        sql.variable(row="input", column=".label.parent"),
                                    ] + [
                                        sql.variable(row="input", column=variable.identifier)
                                        for variable in outputs[label]
                                    ],
                                    from_list=[
                                        sql.named(
                                            sql.name(predecessor.identifier),
                                            name="input",
                                        ),
                                    ],
                                ),
                                sql.select(
                                    select_list=[
                                        sql.variable(row="input", column=".iteration"),
                                        sql.variable(row="input", column=".mark"),
                                        sql.variable(row="input", column=".thread.this"),
                                        sql.variable(row="input", column=".thread.parent"),
                                        sql.variable(row="input", column=".label.parent"),
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
                                        sql.variable(row="input", column=".label.this") + " IS NOT DISTINCT FROM " +
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                                ".done",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.select(
                                select_list=[
                                        sql.variable(row="input", column=".iteration"),
                                        sql.named(
                                            sql.window(
                                                sql.call(
                                                    function="MIN",
                                                    arguments=[
                                                        sql.variable(row="input", column=".mark")
                                                    ]
                                                ),
                                                partition_by=[
                                                    sql.variable(row="input", column=".iteration"),
                                                    sql.variable(row="input", column=".thread.this"),
                                                ],
                                                rows=(
                                                    "UNBOUNDED PRECEDING",
                                                    "UNBOUNDED FOLLOWING"
                                                )
                                            ),
                                            name=".mark"
                                        ),
                                        sql.variable(row="input", column=".thread.this"),
                                        sql.variable(row="input", column=".thread.parent"),
                                        sql.variable(row="input", column=".label.parent"),
                                        sql.named(
                                            sql.prefix_token(
                                                prefix="NOT",
                                                content=sql.call(
                                                    function="EXISTS",
                                                    arguments=[sql.select(
                                                        select_list=[sql.named("1", name="dummy")],
                                                        from_list=[sql.name("loop")],
                                                        predicates=[
                                                            sql.variable(row="loop", column=".mark") + " > " +
                                                            sql.variable(row="input", column=".mark"),
                                                            sql.paren(
                                                                sql.variable(row="loop", column=".thread.this") + " IS NOT DISTINCT FROM " +
                                                                sql.variable(row="input", column=".thread.this") + " OR\n" +
                                                                sql.variable(row="loop", column=".thread.parent") + " IS NOT DISTINCT FROM " +
                                                                sql.variable(row="input", column=".thread.this")
                                                            )
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".label.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.select(
                                select_list=[
                                        sql.variable(row="input", column=".iteration"),
                                        sql.variable(row="input", column=".mark"),
                                        sql.variable(row="input", column=".thread.this"),
                                        sql.named(
                                            sql.string(label.identifier),
                                            name=".label.this"
                                        ),
                                        sql.variable(row="input", column=".thread.parent"),
                                        sql.variable(row="input", column=".label.parent"),
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
                                    "NOT " + sql.variable(row="input", column=".done")
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
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.select(
                                select_list=[
                                        sql.variable(row="input", column=".iteration"),
                                        sql.variable(row="input", column=".mark"),
                                        sql.variable(row="input", column=".thread.this"),
                                        sql.variable(row="input", column=".thread.parent"),
                                        sql.variable(row="input", column=".label.parent"),
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
                                    sql.variable(row="input", column=".done")
                                ]
                            )
                        )
                    )

                case CFG.Call(variables, callee, arguments):
                    assert len(these_predecessors) == 1
                    predecessor = these_predecessors.pop()
                    callee = program.functions[callee]

                    prepare_cte_name = cte_name + ".prepare"
                    ctes.append(
                        sql.cte(
                            name=prepare_cte_name,
                            columns=[
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".label.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                                if variable not in variables
                            ] + [
                                f"argument.{i}"
                                for i in range(len(arguments))
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.variable(row="input", column=".mark"),
                                    sql.named(
                                        sql.paren(
                                            sql.select(
                                                select_list=[
                                                    sql.call(
                                                        function="COALESCE",
                                                        arguments=[
                                                            sql.call(
                                                                function="MAX",
                                                                arguments=[
                                                                    sql.variable(row="loop", column=".thread.this"),
                                                                ]
                                                            ),
                                                            "0"
                                                        ]
                                                    )
                                                ],
                                                from_list=[
                                                    sql.name("loop")
                                                ],
                                                predicates=[
                                                    sql.paren(
                                                        sql.variable(row="loop", column=".label.parent") + " IS NOT DISTINCT FROM " +
                                                        sql.variable(row="input", column=".label.parent") + " OR\n" +
                                                        sql.variable(row="loop", column=".label.this") + " IS NOT DISTINCT FROM " +
                                                        sql.string(label.identifier)
                                                    )
                                                ]
                                            )
                                        )
                                        + " + " +
                                        sql.window(sql.call(function="ROW_NUMBER")),
                                        name=".thread.this"
                                    ),
                                    sql.named(
                                        sql.string(label.identifier),
                                        name=".label.this"
                                    ),
                                    sql.named(
                                        sql.variable(row="input", column=".thread.this"),
                                        name=".thread.parent"
                                    ),
                                    sql.variable(row="input", column=".label.parent"),
                                ] + [
                                    sql.variable(row="input", column=variable.identifier)
                                    for variable in outputs[label]
                                    if variable not in variables
                                ] + [
                                    sql.named(
                                        sql.variable(row="input", column=variable.identifier),
                                        name=f"argument.{i}"
                                    )
                                    for i, variable in enumerate(arguments)
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(predecessor.identifier),
                                        name="input"
                                    )
                                ]
                            )
                        )
                    )
                    sinks.append((
                        prepare_cte_name,
                        set(outputs[label]) - set(variables)
                    ))

                    call_cte_name = cte_name + ".call"
                    ctes.append(
                        sql.cte(
                            name=call_cte_name,
                            columns=[
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".label.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                f"argument.{i}"
                                for i in range(len(arguments))
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.variable(row="input", column=".mark"),
                                    sql.variable(row="input", column=".thread.this"),
                                    sql.named(
                                        sql.string(callee.name.identifier),
                                        name=".label.this"
                                    ),
                                    sql.named(
                                        sql.variable(row="input", column=".thread.this"),
                                        name=".thread.parent"
                                    ),
                                    sql.named(
                                        sql.string(label.identifier),
                                        name=".label.parent"
                                    ),
                                ] + [
                                    sql.variable(row="input", column=f"argument.{i}")
                                    for i in range(len(arguments))
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name(prepare_cte_name),
                                        name="input"
                                    )
                                ]
                            )
                        )
                    )
                    calls.append((
                        call_cte_name,
                        callee.name
                    ))

                    wait_cte_name = cte_name + ".wait"
                    ctes.append(
                        sql.cte(
                            name=wait_cte_name,
                            columns=[
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".label.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                                if variable not in variables
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.variable(row="input", column=".mark"),
                                    sql.variable(row="input", column=".thread.this"),
                                    sql.variable(row="input", column=".label.this"),
                                    sql.variable(row="input", column=".thread.parent"),
                                    sql.variable(row="input", column=".label.parent"),
                                ] + [
                                    sql.named(
                                        sql.variable(row="input", column=f"{function.name.identifier}.{variable.identifier}"),
                                        name=variable.identifier
                                    )
                                    for variable in outputs[label]
                                    if variable not in variables
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name("loop"),
                                        name="input"
                                    )
                                ],
                                predicates=[
                                    sql.variable(row="input", column=".label.this") + " IS NOT DISTINCT FROM " +
                                    sql.string(label.identifier),
                                    sql.call(
                                        function="EXISTS",
                                        arguments=[sql.select(
                                            select_list=[
                                                sql.named("1", name="dummy")
                                            ],
                                            from_list=[
                                                sql.name("loop"),
                                            ],
                                            predicates=[
                                                sql.variable(row="loop", column=".label.this") + " IS NOT NULL",
                                                sql.variable(row="loop", column=".label.parent") + " IS NOT DISTINCT FROM " +
                                                sql.string(label.identifier),
                                                sql.paren(
                                                    sql.variable(row="loop", column=".thread.this") + " IS NOT DISTINCT FROM " +
                                                    sql.variable(row="input", column=".thread.this") + " AND\n" +
                                                    sql.variable(row="loop", column=".thread.parent") + " IS NULL OR\n" +
                                                    sql.variable(row="loop", column=".thread.parent") + " IS NOT DISTINCT FROM " +
                                                    sql.variable(row="input", column=".thread.this")
                                                )
                                            ]
                                        )]
                                    )
                                ]
                            )
                        )
                    )
                    sinks.append((
                        wait_cte_name,
                        set(outputs[label]) - set(variables)
                    ))

                    ctes.append(
                        sql.cte(
                            name=cte_name,
                            columns=[
                                ".iteration",
                                ".mark",
                                ".thread.this",
                                ".thread.parent",
                                ".label.parent",
                            ] + [
                                variable.identifier
                                for variable in outputs[label]
                            ],
                            body=sql.select(
                                select_list=[
                                    sql.variable(row="input", column=".iteration"),
                                    sql.variable(row="input", column=".mark"),
                                    sql.variable(row="input", column=".thread.parent"),
                                    sql.variable(row="input", column=".thread.parent"),
                                    sql.variable(row="input", column=".label.parent"),
                                ] + [
                                    sql.named(
                                        (
                                            sql.variable(
                                                row="return",
                                                column=f"{callee.name.identifier}.result.{variables.index(variable)}"
                                            )
                                            if variable in variables else
                                            sql.variable(
                                                row="input",
                                                column=f"{function.name.identifier}.{variable.identifier}"
                                            )
                                        ),
                                        name=variable.identifier
                                    )
                                    for variable in outputs[label]
                                ],
                                from_list=[
                                    sql.named(
                                        sql.name("loop"),
                                        name="input"
                                    ),
                                    sql.named(
                                        sql.name("loop"),
                                        name="return"
                                    )
                                ],
                                predicates=[
                                    sql.variable(row="input", column=".label.this") + " IS NOT DISTINCT FROM " +
                                    sql.string(label.identifier),
                                    sql.variable(row="return", column=".label.this") + " IS NULL",
                                    sql.variable(row="return", column=".label.parent") + " IS NOT DISTINCT FROM " +
                                    sql.string(label.identifier),
                                    sql.variable(row="return", column=".thread.parent") + " IS NOT DISTINCT FROM " +
                                    sql.variable(row="input", column=".thread.this"),
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
                    sql.NULL,
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
                        sql.NULL,
                        symbol_table[variable].source
                    ),
                    name=f"{function.name.identifier}.{variable.identifier}",
                )
                for variable in loop_carried_variables
            )
            init_list.extend(
                sql.named(
                    sql.cast(
                        sql.NULL,
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
                sql.named(sql.name(name), name="sink"),
                [
                    sql.variable(row="sink", column=".iteration") + " + 1",
                    sql.variable(row="sink", column=".mark"),
                    sql.variable(row="sink", column=".thread.this"),
                    sql.variable(row="sink", column=".label.this"),
                    sql.variable(row="sink", column=".thread.parent"),
                    sql.variable(row="sink", column=".label.parent"),
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
                                sql.NULL,
                                symbol_table[variable].source
                            ),
                            name=f"{function.name.identifier}.{variable.identifier}"
                        )
                        for variable in loop_carried_variables
                    ),
                    *(
                        sql.named(
                            sql.cast(
                                sql.NULL,
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
                    sql.variable(row="emit", column=".iteration") + " + 1",
                    sql.variable(row="emit", column=".mark"),
                    sql.named(
                        sql.cast(sql.NULL, "INT"),
                        name=".thread.this"
                    ),
                    sql.named(
                        sql.cast(sql.NULL, "TEXT"),
                        name=".label.this"
                    ),
                    sql.variable(row="emit", column=".thread.parent"),
                    sql.variable(row="emit", column=".label.parent"),
                ] +
                loop_column_prefix +
                [
                    *(
                        sql.named(
                            sql.cast(
                                sql.NULL,
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

    for caller, callee in calls:
        called_function = program.functions[callee]
        symbol_table = symbol_tables[callee]

        data_columns = []
        for column in loop_schema[6:]:
            origin_function, variable_name = column.split(".", maxsplit=1)
            variable = common.Identifier(variable_name, annotation=None)
            origin_function = program.functions[common.Identifier(origin_function, annotation=None)]

            data_columns.append(
                sql.named(
                    sql.variable(
                        row="caller",
                        column=f"argument.{list(called_function.parameters.keys()).index(variable)}"
                    )
                    if origin_function.name == called_function.name and variable in origin_function.parameters else
                    sql.cast(
                        sql.NULL,
                        type=symbol_tables[origin_function.name][
                            common.Identifier(variable_name, annotation=None)
                        ].source,
                    )
                    if not variable_name.startswith("result.") else
                    sql.cast(
                        sql.NULL,
                        type=origin_function.return_types[int(variable_name[7:])].source,
                    )
                    ,
                    name=column
                )
            )

        collector_data.append(
            (
                sql.named(sql.name(caller), name="caller"),
                [
                    sql.variable(row="caller", column=".iteration") + " + 1",
                    sql.variable(row="caller", column=".mark"),
                    sql.variable(row="caller", column=".thread.this"),
                    sql.variable(row="caller", column=".label.this"),
                    sql.variable(row="caller", column=".thread.parent"),
                    sql.variable(row="caller", column=".label.parent"),
                ] + data_columns
            )
        )

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
                sql.variable(row="loop", column=".thread.this") + " IS NULL",
                sql.variable(row="loop", column=".label.this") + " IS NULL",
                sql.variable(row="loop", column=".thread.parent") + " = 0",
                sql.variable(row="loop", column=".label.parent") + " IS NULL",
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
