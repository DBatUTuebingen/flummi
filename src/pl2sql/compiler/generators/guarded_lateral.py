from typing import override

from .lateral import LateralGenerator
from .. import names
from ...IR import CFP
from ...library import sql, graph


class GuardedLateralGenerator(LateralGenerator, name="guarded_lateral"):
    @override
    def generate(self) -> sql.SQL:
        cfp = self.program.body
        predecessors = graph.invert(cfp.transitions)

        from_list = [
            self.generate_primitive(
                label, cfp.primitives[label], predecessors[label]
            )
            for label in graph.topological_order(cfp.transitions)
        ]

        from_list.append(
            sql.named(
                sql.lateral(
                    sql.union_all(
                        [
                            sql.select(
                                [sql.variable(names.result, label.identifier)],
                                predicates=[
                                    sql.variable(
                                        names.guard,
                                        self.flow.guard_of[label].identifier,
                                    )
                                    + " IS NOT DISTINCT FROM TRUE"
                                ],
                            )
                            for label, primitive in cfp.primitives.items()
                            if isinstance(primitive, CFP.Emit)
                        ]
                    )
                ),
                names.result,
                columns=[names.result],
            )
        )

        return (
            sql.select(
                select_list=[sql.variable(names.result, names.result)],
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
                return sql.named(
                    sql.paren(
                        sql.select(
                            select_list=["true"],
                        )
                    ),
                    label.identifier,
                    [names.guard],
                )

            case CFP.Let(variable, expression):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]
                return sql.named(
                    sql.lateral(
                        sql.select(
                            select_list=[
                                sql.case(
                                    sql.when(
                                        sql.variable(
                                            names.guard,
                                            self.flow.guard_of[
                                                label
                                            ].identifier,
                                        ),
                                        expression.source.format(
                                            *(
                                                sql.paren(
                                                    sql.variable(
                                                        argument.identifier,
                                                        self.flow.definitions_after[
                                                            predecessor
                                                        ][argument].identifier,
                                                    )
                                                )
                                                for argument in expression.arguments
                                            )
                                        ),
                                    ),
                                    default="NULL",
                                ),
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
                                sql.variable(
                                    variable.identifier,
                                    self.flow.definitions_after[predecessor][
                                        variable
                                    ].identifier,
                                ),
                            ],
                        )
                    ),
                    label.identifier,
                    columns=[names.result],
                )

            case CFP.Where(variable) | CFP.WhereNot(variable):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]
                return sql.named(
                    sql.lateral(
                        sql.select(
                            select_list=[
                                sql.variable(
                                    names.guard,
                                    self.flow.guard_of[label].identifier,
                                )
                                + " AND "
                                + sql.variable(
                                    variable.identifier,
                                    self.flow.definitions_after[predecessor][
                                        variable
                                    ].identifier,
                                )
                                + " IS NOT DISTINCT FROM "
                                + (
                                    "TRUE"
                                    if isinstance(primitive, CFP.Where)
                                    else "FALSE"
                                ),
                            ],
                        )
                    ),
                    label.identifier,
                    columns=[names.guard],
                )

            case CFP.Merge():
                return sql.named(
                    sql.lateral(
                        sql.union_all(
                            [
                                sql.select(
                                    select_list=[
                                        sql.variable(
                                            variable.identifier,
                                            self.flow.definitions_after[
                                                predecessor
                                            ][variable].identifier,
                                        )
                                        for variable in sorted(
                                            self.flow.definitions_after[label]
                                        )
                                    ],
                                    predicates=[
                                        sql.variable(
                                            names.guard,
                                            self.flow.guard_of[
                                                predecessor
                                            ].identifier,
                                        )
                                    ],
                                )
                                for predecessor in sorted(predecessors)
                            ]
                        )
                    ),
                    label.identifier,
                    columns=[
                        variable.identifier
                        for variable in sorted(
                            self.flow.definitions_after[label]
                        )
                    ],
                )

            case _:
                return super().generate_primitive(
                    label, primitive, predecessors
                )
