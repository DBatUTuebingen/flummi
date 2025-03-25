from . import names
from ..IR import CFG, common
from ..library import sql, graph


__all__ = (
    "codegen",
)


class Kind:
    DATA = sql.string("data")
    MEMO = sql.string("memo")
    STACK_FRAME = sql.string("frame")


def codegen(
    cfg: CFG.Graph,
    #? [info] data flow
    outputs: dict[common.Identifier, set[common.Identifier]],
    #? [info] allocation
    registers: dict[str, common.Type],
    register_allocations: dict[common.Identifier, dict[str, common.Identifier]],
    variable_allocations: dict[common.Identifier, dict[common.Identifier, str]],
    result_allocation: dict[common.Identifier|None, str],
    #? [info] config
    explicit_materialized: bool = False,
    avoid_multiple_recursive_references: bool = False,
    keep_stackframes_alive: bool = True,
    keep_memos_alive: bool = True,
) -> str:
    predecessors = graph.invert(cfg.edges)

    working_table_writers = []
    ctes = []

    working_table_schema: dict[str, str] = {
        names.iteration: "INT",
        names.kind: "TEXT",
        names.label: "TEXT",
    }

    if keep_stackframes_alive:
        working_table_schema |= {
            names.return_label: "TEXT",
            names.depth: "INT",
        }

    working_table_schema |= {
        register: type.source
        for register, type in registers.items()
    }

    if avoid_multiple_recursive_references:
        ctes.append(
            sql.cte(
                name=names.working_table,
                columns=list(working_table_schema),
                body=sql.select(
                    select_list=list(working_table_schema),
                    from_list=[sql.name(names.working_table)]
                )
            )
        )

    for name, node in cfg.nodes.items():
        match node:
            case CFG.Let(variable, expression):
                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 1
                predecessor = list(these_predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.paren(
                                expression.source.format(*(
                                    sql.paren(sql.variable(argument.identifier, "p"))
                                    for argument in expression.arguments
                                ))
                            )
                            if output == variable else
                            sql.variable(output.identifier, "p"),
                            output.identifier
                        )
                        for output in outputs[name]
                    ],
                    from_list=[
                        sql.named(sql.name(predecessor.identifier), "p")
                    ]
                )

            case CFG.Return(function, variable):
                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 1
                predecessor = list(these_predecessors)[0]

                working_table_writers.append(name)

                body = sql.select(
                    select_list=[
                        sql.named(
                            Kind.DATA
                            if column == names.kind else
                            sql.variable(column,"p")
                            if column in {names.iteration, names.depth, names.return_label} else
                            sql.variable(variable.identifier,"p")
                            if column == result_allocation[function] else
                            sql.cast("NULL", type),
                            column
                        )
                        for column, type in working_table_schema.items()
                    ],
                    from_list=[
                        sql.named(sql.name(predecessor.identifier), "p")
                    ],
                )

            case CFG.Where(variable):
                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 1
                predecessor = list(these_predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.variable(output.identifier, "p")
                        for output in outputs[name]
                    ],
                    from_list=[
                        sql.named(sql.name(predecessor.identifier), "p")
                    ],
                    predicates=[
                        sql.variable(variable.identifier, "p")
                    ]
                )

            case CFG.WhereNot(variable):
                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 1
                predecessor = list(these_predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.variable(output.identifier, "p")
                        for output in outputs[name]
                    ],
                    from_list=[
                        sql.named(sql.name(predecessor.identifier), "p")
                    ],
                    predicates=[
                        "NOT " + sql.variable(variable.identifier, "p")
                    ]
                )

            case CFG.Merge():
                body = sql.union_all([
                    sql.select(
                        select_list=[
                            sql.variable(output.identifier, "p")
                            for output in outputs[name]
                        ],
                        from_list=[
                            sql.named(sql.name(predecessor.identifier), "p")
                        ],
                    )
                    for predecessor in predecessors[name]
                ])

            case CFG.Push(label):
                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 1
                predecessor = list(these_predecessors)[0]

                working_table_writers.append(name)

                body = sql.select(
                    select_list=[
                        sql.named(
                            Kind.STACK_FRAME
                            if column == names.kind else
                            sql.string(label.identifier)
                            if column == names.label else
                            sql.variable(variable.identifier, "p")
                            if (variable := register_allocations[label].get(column)) is not None else
                            sql.cast("NULL", type),
                            column
                        )
                        for column, type in working_table_schema.items()
                    ],
                    from_list=[
                        sql.named(sql.name(predecessor.identifier), "p")
                    ],
                )

            case CFG.Pop(label):
                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 0

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.variable(variable_allocations[label][output], "p"),
                            output.identifier
                        )
                        for output in outputs[name]
                    ],
                    from_list=[
                        sql.named(sql.name(names.working_table), "p")
                    ],
                    predicates=[
                        sql.string(label.identifier) + " = " +
                        sql.variable(names.label, "p"),
                        Kind.STACK_FRAME + " = " +
                        sql.variable(names.kind, "p"),
                    ]
                )

            case CFG.Link(label):
                assert keep_stackframes_alive

                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 1
                predecessor = list(these_predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.string(label.identifier)
                            if output.identifier == names.return_label else
                            sql.variable(output.identifier, "p") + " + 1"
                            if output.identifier == names.depth else
                            sql.variable(output.identifier, "p"),
                            output.identifier
                        )
                        for output in outputs[name]
                    ],
                    from_list=[
                        sql.named(sql.name(predecessor.identifier), "p")
                    ],
                )

            case CFG.Resume(function, variable):
                assert keep_stackframes_alive

                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 1
                predecessor = list(these_predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.variable(result_allocation[function], "d")
                            if variable == output else
                            sql.variable(output.identifier, "p"),
                            output.identifier
                        )
                        for output in outputs[name]
                    ],
                    from_list=[
                        sql.named(sql.name(predecessor.identifier), "p"),
                        sql.named(sql.name(names.working_table), "d"),
                    ],
                    predicates=[
                        Kind.DATA + " = " +
                        sql.variable(names.kind, "d"),
                        sql.variable(names.return_label, "d") + " = " +
                        sql.variable(names.label, "p"),
                        sql.variable(names.depth, "d") + " - 1 = " +
                        sql.variable(names.depth, "p"),
                    ]
                )

            case CFG.Lookup(result, hit, function, arguments):
                assert keep_memos_alive

                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 1
                predecessor = list(these_predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.variable(result_allocation[function], "m")
                            if output == result else
                            sql.variable(names.kind, "m") + " IS NOT NULL"
                            if output == hit else
                            sql.variable(output.identifier, "p"),
                            output.identifier
                        )
                        for output in outputs[name]
                    ],
                    from_list=[
                        sql.named(sql.name(predecessor.identifier), "p") +
                        sql.join(
                            "LEFT OUTER",
                            sql.named(sql.name(names.working_table), "m"),
                            [
                                Kind.MEMO + " = " +
                                sql.variable(names.kind, "m"),
                            ] + [
                                sql.variable(parameter.identifier, "m") + " = " +
                                sql.variable(argument.identifier, "p")
                                for parameter, argument in arguments.items()
                            ]
                        )
                    ],
                )

            case CFG.Memoize(function, arguments, value):
                assert keep_memos_alive

                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 1
                predecessor = list(these_predecessors)[0]

                working_table_writers.append(name)

                #! [warn] For some reason dictionary lookups using the
                #!        Identifier objects is simply broken; same hash, same
                #!        value, everything, but stil...
                arguments = {
                    p.identifier: a.identifier
                    for p, a in arguments.items()
                }

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.variable(names.iteration, "p")
                            if column == names.iteration else
                            Kind.MEMO
                            if column == names.kind else
                            sql.variable(value.identifier, "p")
                            if column == result_allocation[function] else
                            sql.variable(argument, "p")
                            if (parameter := register_allocations[function].get(column)) and
                               (argument := arguments.get(parameter.identifier)) else
                            sql.cast("NULL", type),
                            column
                        )
                        for column, type in working_table_schema.items()
                    ],
                    from_list=[
                        sql.named(sql.name(predecessor.identifier), "p")
                    ],
                )

            case _:
                raise NotImplementedError()

        ctes.append(
            sql.cte(
                name=name.identifier,
                columns=(
                    list(working_table_schema)
                    if name in working_table_writers else
                    [
                        output.identifier
                        for output in outputs[name]
                    ]
                ),
                body=body,
                materialize=explicit_materialized and len(cfg.edges[name]) > 1
            )
        )

    working_table_writes = [
        sql.select(
            select_list=[
                sql.variable(column, "w") + " + 1"
                if column == names.iteration else
                sql.variable(column, "w")
                for column in working_table_schema
            ],
            from_list=[sql.named(sql.name(writer.identifier), "w")]
        )
        for writer in working_table_writers
    ]

    keep_alives = []

    if keep_memos_alive:
        keep_alives.append(
            sql.select(
                distinct=True,
                select_list=[
                    sql.variable(column, "m") + " + 1"
                    if column == names.iteration else
                    sql.variable(column, "m")
                    for column in working_table_schema
                ],
                from_list=[
                    sql.named(sql.name(names.working_table), "m"),
                    sql.named(sql.name(names.working_table), "f"),
                ],
                predicates=[
                    Kind.MEMO + " = " +
                    sql.variable(names.kind, "m"),
                    sql.variable(names.label, "f") + " IS NOT NULL",
                ]
            )
        )

    if keep_stackframes_alive:
        keep_alives.append(
            sql.select(
                select_list=[
                    sql.variable(column, "c") + " + 1"
                    if column == names.iteration else
                    sql.variable(column, "c")
                    for column in working_table_schema
                ],
                from_list=[
                    sql.named(sql.name(names.working_table), "c"),
                    sql.named(sql.name(names.working_table), "o"),
                ],
                predicates=[
                    Kind.STACK_FRAME + " = " +
                    sql.variable(names.kind, "c"),
                    Kind.STACK_FRAME + " = " +
                    sql.variable(names.kind, "o"),
                    sql.variable(names.return_label, "o") + " = " +
                    sql.variable(names.label, "c"),
                    sql.variable(names.depth, "o") + " - " +
                    sql.variable(names.depth, "c") + " = 1",
                ]
            )
        )

    recursive_anchor = sql.with_ctes(
        ctes=ctes,
        body=sql.union_all(working_table_writes + keep_alives)
    )

    base_anchor = sql.select(
        select_list=[
            sql.named(
                sql.cast('0', "INT")
                if column == names.iteration else
                Kind.STACK_FRAME
                if column == names.kind else
                sql.string(cfg.entry_label.identifier)
                if column == names.label else
                sql.cast("NULL", "TEXT")
                if column == names.return_label else
                "0"
                if column == names.depth else
                sql.variable(variable.identifier)
                if (variable := register_allocations[cfg.entry_label].get(column)) is not None else
                sql.cast("NULL", type),
                column
            )
            for column, type in working_table_schema.items()
        ]
    )

    recursive_cte = sql.cte(
        name=names.working_table,
        columns=list(working_table_schema),
        body=sql.union_all([base_anchor, recursive_anchor])
    )

    extract_results = sql.select(
        select_list=[
            sql.variable(result_allocation[None], "p")
        ],
        from_list=[
            sql.named(sql.name(names.working_table), "p")
        ],
        predicates=[
            sql.variable(names.kind, "p") + " = " + Kind.DATA,
            sql.variable(names.label, "p") + " IS NULL",
            sql.variable(names.depth, "p") + " = 0"
        ]
    )

    return sql.with_ctes(
        recursive=True,
        ctes=[recursive_cte],
        body=extract_results
    )
