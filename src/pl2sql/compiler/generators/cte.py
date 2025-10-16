from typing import override

from .base import Generator
from .. import names
from ...IR import CFP
from ...library import sql, graph


class CTEGenerator(Generator, name="CTE"):
    @override
    def generate_program(self, program: CFP.Program) -> sql.SQL:
        cfp = program.body
        predecessors = graph.invert(cfp.transitions)

        ctes = [
            self.generate_primitive(
                label,
                cfp.primitives[label],
                predecessors[label],
            )
            for label in graph.topological_order(cfp.transitions)
        ]

        return (
            sql.with_ctes(
                ctes=ctes,
                body=sql.union_all(
                    [
                        sql.select(
                            select_list=[
                                sql.variable(names.result, label.identifier)
                            ],
                            from_list=[sql.name(label.identifier)],
                        )
                        for label, primitive in cfp.primitives.items()
                        if isinstance(primitive, CFP.Emit)
                    ]
                ),
            )
            + ";"
        )

    @override
    def generate_primitive(
        self,
        label: CFP.Label,
        primitive: CFP.Primitive,
        predecessors: set[CFP.Label],
    ) -> sql.SQL:
        outputs = [
            variable.identifier for variable in self.dataflow.outputs_of[label]
        ] or [names.nothing]

        match primitive:
            case CFP.Start():
                assert len(predecessors) == 0

                body = sql.select(
                    select_list=[
                        sql.named(
                            "NULL",
                            output,
                        )
                        for output in outputs
                    ],
                )

            case CFP.Let(variable, expression):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.paren(
                                expression.source.format(
                                    *(
                                        sql.paren(
                                            sql.variable(
                                                argument.identifier,
                                                predecessor.identifier,
                                            )
                                        )
                                        for argument in expression.arguments
                                    )
                                )
                            )
                            if output == variable.identifier
                            else sql.variable(output, predecessor.identifier),
                            output,
                        )
                        for output in outputs
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                )

            case CFP.Emit(variable):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.variable(
                                variable.identifier, predecessor.identifier
                            )
                            if output == names.result
                            else sql.variable(output, predecessor.identifier),
                            output,
                        )
                        for output in outputs
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                )

            case CFP.Merge():
                assert len(predecessors) > 1

                body = sql.union_all(
                    [
                        sql.select(
                            select_list=[
                                sql.named(
                                    "NULL"
                                    if output == names.nothing
                                    else sql.variable(
                                        output,
                                        predecessor.identifier,
                                    ),
                                    output,
                                )
                                for output in outputs
                            ],
                            from_list=[sql.name(predecessor.identifier)],
                        )
                        for predecessor in predecessors
                    ]
                )

            case CFP.Where(condition) | CFP.WhereNot(condition):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            "NULL"
                            if output == names.nothing
                            else sql.variable(
                                output,
                                predecessor.identifier,
                            ),
                            output,
                        )
                        for output in outputs
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                    predicates=[
                        sql.variable(
                            condition.identifier, predecessor.identifier
                        )
                        + " IS NOT DISTINCT FROM "
                        + (
                            "TRUE"
                            if isinstance(primitive, CFP.Where)
                            else "FALSE"
                        )
                    ],
                )

            case _:
                return super().generate_primitive(
                    label, primitive, predecessors
                )

        return sql.cte(
            name=label.identifier,
            columns=outputs,
            body=body,
        )
