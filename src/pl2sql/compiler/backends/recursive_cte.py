from typing import override

from .base import UseColumnAllocation
from .cte import CTEGenerator
from .. import constants
from ..features import Features
from ...IR import CFP
from ...library import sql, graph


class RecursiveCTEGenerator(
    UseColumnAllocation,
    CTEGenerator,
    name="recursive_cte",
    supports=Features.SEQUENCING | Features.BRANCHING | Features.ITERATION,
):
    @override
    def generate(self) -> sql.SQL:
        cfp = self.program.body
        predecessors = graph.invert(cfp.edges)

        ctes: list[sql.SQL] = []
        working_table_writes: list[sql.SQL] = []
        for label in graph.topological_order(cfp.edges):
            primitive = cfp.primitives[label]

            ctes.append(
                self.generate_primitive(
                    label,
                    primitive,
                    predecessors[label],
                )
            )

            match primitive:  # pyright: ignore[reportMatchNotExhaustive]
                case CFP.GoTo(target_label):
                    allocation = self.allocation_for[target_label]
                    working_table_writes.append(
                        sql.select(
                            select_list=[
                                sql.named(
                                    sql.cast(
                                        (
                                            sql.NULL
                                            if (
                                                variable
                                                := allocation.variable_at(
                                                    column
                                                )
                                            )
                                            is None
                                            else sql.variable(
                                                variable.identifier,
                                                label.identifier,
                                            )
                                        ),
                                        type.source,
                                    ),
                                    column,
                                )
                                for column, type in self.schema.items()
                            ],
                            from_list=[sql.name(label.identifier)],
                        )
                    )

                case CFP.Emit(_):
                    working_table_writes.append(
                        sql.select(
                            select_list=[
                                sql.named(
                                    sql.cast(
                                        (
                                            sql.variable(
                                                constants.Names.RESULT,
                                                label.identifier,
                                            )
                                            if column == constants.Names.RESULT
                                            else sql.NULL
                                        ),
                                        type.source,
                                    ),
                                    column,
                                )
                                for column, type in self.schema.items()
                            ],
                            from_list=[sql.name(label.identifier)],
                        )
                    )

        recursive_anchor = sql.with_ctes(
            ctes=ctes, body=sql.union_all(working_table_writes)
        )

        base_anchor = sql.select(
            select_list=[
                sql.named(
                    sql.cast(
                        (
                            sql.string(self.program.body.entry_label.identifier)
                            if column == constants.Names.LABEL
                            else sql.NULL
                        ),
                        type.source,
                    ),
                    column,
                )
                for column, type in self.schema.items()
            ]
        )

        recursive_cte = sql.cte(
            name=constants.Names.WORKING_TABLE,
            columns=list(self.schema),
            body=sql.union_all([base_anchor, recursive_anchor]),
        )

        result_selection = sql.select(
            select_list=[
                sql.variable(
                    constants.Names.RESULT, constants.Names.WORKING_TABLE
                )
            ],
            from_list=[sql.name(constants.Names.WORKING_TABLE)],
            predicates=[
                sql.variable(
                    constants.Names.LABEL, constants.Names.WORKING_TABLE
                )
                + " IS NULL"
            ],
        )

        return (
            sql.with_ctes(
                ctes=[recursive_cte], recursive=True, body=result_selection
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
                assert len(predecessors) == 0

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.NULL,
                            constants.Names.NOTHING,
                        ),
                        *(
                            sql.named(
                                sql.variable(
                                    str(
                                        self.allocation_for[label].column_for(
                                            output
                                        )
                                    ),
                                    constants.Names.WORKING_TABLE,
                                ),
                                output.identifier,
                            )
                            for output in self.outputs_of[label]
                        ),
                    ],
                    from_list=[sql.name(constants.Names.WORKING_TABLE)],
                    predicates=[
                        sql.variable(
                            constants.Names.LABEL, constants.Names.WORKING_TABLE
                        )
                        + " IS NOT DISTINCT FROM "
                        + sql.string(label.identifier)
                    ],
                )

            case CFP.GoTo(target_label):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.NULL,
                            constants.Names.NOTHING,
                        ),
                        *(
                            sql.named(
                                sql.string(target_label.identifier),
                                constants.Names.LABEL,
                            )
                            if output.identifier == constants.Names.LABEL
                            else sql.named(
                                sql.variable(
                                    output.identifier,
                                    predecessor.identifier,
                                ),
                                output.identifier,
                            )
                            for output in self.outputs_of[label]
                        ),
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                )

            case _:
                return super().generate_primitive(
                    label, primitive, predecessors
                )

        return sql.cte(
            name=label.identifier,
            columns=[
                constants.Names.NOTHING,
                *(variable.identifier for variable in self.outputs_of[label]),
            ],
            body=body,
        )
