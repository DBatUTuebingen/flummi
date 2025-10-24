from typing import override

from .base import PrimitiveBackend, UseGuards, UseReachingDefinitions
from .. import constants
from ...IR import CFP
from ...library import sql, graph


class LateralGenerator(
    UseGuards, UseReachingDefinitions, PrimitiveBackend, name="lateral"
):
    @override
    def generate(self) -> sql.SQL:
        cfp = self.program.body
        predecessors = graph.invert(cfp.edges)

        from_list = [
            self.generate_primitive(
                label, cfp.primitives[label], predecessors[label]
            )
            for label in graph.topological_order(cfp.edges)
        ]

        from_list.append(
            sql.named(
                sql.lateral(
                    sql.union_all(
                        [
                            sql.select(
                                [
                                    sql.variable(
                                        constants.Names.RESULT, label.identifier
                                    )
                                ]
                            )
                            for label, primitive in cfp.primitives.items()
                            if isinstance(primitive, CFP.Emit)
                        ]
                    )
                ),
                constants.Names.RESULT,
                columns=[constants.Names.RESULT],
            )
        )

        return (
            sql.select(
                select_list=[
                    sql.variable(constants.Names.RESULT, constants.Names.RESULT)
                ],
                from_list=from_list,
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
        match primitive:
            case CFP.Start():
                assert not predecessors
                return sql.paren(
                    sql.select(
                        select_list=[
                            sql.named(sql.NULL, constants.Names.NOTHING)
                        ],
                    )
                )

            case CFP.Let(variable, expression):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]
                return sql.named(
                    sql.lateral(
                        sql.select(
                            select_list=[
                                expression.source.format(
                                    *(
                                        sql.paren(
                                            sql.variable(
                                                argument.identifier,
                                                self.definitions_after[
                                                    predecessor
                                                ][argument].identifier,
                                            )
                                        )
                                        for argument in expression.arguments
                                    )
                                )
                            ]
                        )
                    ),
                    label.identifier,
                    columns=[variable.identifier],
                )

            case CFP.Emit(variable):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]
                return sql.named(
                    sql.lateral(
                        sql.select(
                            select_list=[
                                sql.named(
                                    sql.variable(
                                        variable.identifier,
                                        self.definitions_after[predecessor][
                                            variable
                                        ].identifier,
                                    ),
                                    constants.Names.RESULT,
                                )
                            ],
                        )
                    ),
                    label.identifier,
                    columns=[constants.Names.RESULT],
                )

            case _:
                return super().generate_primitive(
                    label, primitive, predecessors
                )
