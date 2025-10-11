from . import names
from ..IR import CFP, common
from ..library import sql, graph


__all__ = ("codegen",)


def codegen(
    program: CFP.Program,
    # ? [info] data flow
    outputs: dict[common.Identifier, set[common.Identifier]],
) -> str:
    cfp = program.body

    predecessors = graph.invert(cfp.edges)

    output_writers: list[CFP.Label] = []
    ctes: list[sql.SQL] = []

    for name, node in cfp.nodes.items():
        match node:
            case CFP.Start():
                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 0

                body = sql.select(
                    select_list=[
                        sql.named(
                            "NULL",
                            output.identifier,
                        )
                        for output in outputs[name]
                    ],
                )

            case CFP.Let(variable, expression):
                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 1
                predecessor = list(these_predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.paren(
                                expression.source.format(
                                    *(
                                        sql.paren(
                                            sql.variable(
                                                argument.identifier, "p"
                                            )
                                        )
                                        for argument in expression.arguments
                                    )
                                )
                            )
                            if output == variable
                            else sql.variable(output.identifier, "p"),
                            output.identifier,
                        )
                        for output in outputs[name]
                    ],
                    from_list=[
                        sql.named(sql.name(predecessor.identifier), "p")
                    ],
                )

            case CFP.Emit(variable):
                these_predecessors = predecessors[name]
                assert len(these_predecessors) == 1
                predecessor = list(these_predecessors)[0]

                output_writers.append(name)

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.variable(variable.identifier, "p")
                            if output.identifier == names.result
                            else sql.variable(output.identifier, "p"),
                            output.identifier,
                        )
                        for output in outputs[name]
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
                columns=[output.identifier for output in outputs[name]],
                body=body,
            )
        )

    output_writes = [
        sql.select(
            select_list=[sql.variable(names.result, "w")],
            from_list=[sql.named(sql.name(writer.identifier), "w")],
        )
        for writer in output_writers
    ]

    return sql.with_ctes(ctes=ctes, body=sql.union_all(output_writes))
