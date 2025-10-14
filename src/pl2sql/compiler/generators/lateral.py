from typing import override

from .base import Generator
from .. import names
from ...IR import CFP
from ...library import sql, graph


class LateralGenerator(Generator, name="lateral"):
    @override
    def generate_program(self, program: CFP.Program) -> sql.SQL:
        cfp = program.body
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
                                [sql.variable(names.result, label.identifier)]
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
                return sql.paren(
                    sql.select(
                        select_list=[sql.named("NULL", names.nothing)],
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
                                                self.dataflow.binding_sites_at[
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
                                        self.dataflow.binding_sites_at[
                                            predecessor
                                        ][variable].identifier,
                                    ),
                                    names.result,
                                )
                            ],
                        )
                    ),
                    label.identifier,
                    columns=[names.result],
                )

            case _:
                return super().generate_primitive(
                    label, primitive, predecessors
                )
