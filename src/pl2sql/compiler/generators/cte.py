from typing import override

from .base import PrimitiveGenerator
from .. import constants
from ...IR import CFP
from ...library import sql, graph


class CTEGenerator(PrimitiveGenerator, name="CTE"):
    @override
    def generate(self) -> sql.SQL:
        cfp = self.program.body
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
                                sql.variable(
                                    constants.Names.RESULT, label.identifier
                                )
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
            variable.identifier for variable in self.flow.outputs_of[label]
        ] or [constants.Names.NOTHING]

        match primitive:
            case CFP.Start():
                assert len(predecessors) == 0

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.NULL,
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
                            if output == constants.Names.RESULT
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
                                    sql.NULL
                                    if output == constants.Names.NOTHING
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
                            sql.NULL
                            if output == constants.Names.NOTHING
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
