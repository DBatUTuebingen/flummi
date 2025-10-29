from typing import override

from .mixins import UseStartAllocation, UseLiveVariables
from .cte import CTEBackend
from .. import constants
from ..features import Feature
from ...IR import CFP
from ...library import sql, graph


class RecursiveCTEGenerator(
    CTEBackend,
    UseStartAllocation,
    UseLiveVariables,
    name="recursive_cte",
    supports={
        Feature.SEQUENCING,
        Feature.BRANCHING,
        Feature.ITERATION,
        Feature.CONCURRENCY,
    },
):
    @override
    def generate(self) -> sql.SQL:
        ctes: list[sql.SQL] = []
        working_table_writes: list[sql.SQL] = []
        for label in graph.topological_order(self.successors_of):
            primitive = self.primitives[label]

            ctes.append(self.generate_primitive(label))

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
    def generate_primitive(self, label: CFP.Label) -> sql.SQL:
        primitive = self.primitives[label]
        predecessors = self.predecessors_of[label]

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
                        + " = "
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
                                sql.string(target_label.identifier)
                                if output.identifier == constants.Names.LABEL
                                else sql.variable(
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

            case CFP.Fork(variables, expression):
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
                                sql.variable(
                                    output.identifier,
                                    constants.Names.EXPRESSION,
                                )
                                if output in variables
                                else sql.variable(
                                    output.identifier, predecessor.identifier
                                ),
                                output.identifier,
                            )
                            for output in self.outputs_of[label]
                        ),
                    ],
                    from_list=[
                        sql.name(predecessor.identifier),
                        sql.named(
                            sql.lateral(
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
                            ),
                            constants.Names.EXPRESSION,
                            [variable.identifier for variable in variables],
                        ),
                    ],
                )

            case CFP.SiblingProbe(variable, sibling_label, keys):
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
                                (
                                    sql.call(
                                        "NOT EXISTS ",
                                        [
                                            sql.paren(
                                                sql.select(
                                                    select_list=[
                                                        sql.named(
                                                            sql.NULL,
                                                            constants.Names.NOTHING,
                                                        )
                                                    ],
                                                    from_list=[
                                                        sql.name(
                                                            constants.Names.WORKING_TABLE
                                                        )
                                                    ],
                                                    predicates=[
                                                        sql.variable(
                                                            constants.Names.LABEL,
                                                            constants.Names.WORKING_TABLE,
                                                        )
                                                        + " <> "
                                                        + sql.string(
                                                            sibling_label.identifier
                                                        ),
                                                        *(
                                                            sql.variable(
                                                                column,
                                                                constants.Names.WORKING_TABLE,
                                                            )
                                                            + " = "
                                                            + sql.variable(
                                                                key.identifier,
                                                                predecessor.identifier,
                                                            )
                                                            for key in keys
                                                            if (
                                                                column
                                                                := self.allocation_for[
                                                                    sibling_label
                                                                ].column_for(
                                                                    key
                                                                )
                                                            )
                                                            is not None
                                                        ),
                                                    ],
                                                )
                                            )
                                        ],
                                    )
                                )
                                if output == variable
                                else sql.variable(
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

            case CFP.Gather(aggregates, keys):
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
                                if (expression := aggregates.get(output))
                                is not None
                                else sql.variable(
                                    output.identifier,
                                    predecessor.identifier,
                                )
                                if output in keys
                                else sql.NULL,
                                output.identifier,
                            )
                            for output in self.outputs_of[label]
                        ),
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                    group_keys=[variable.identifier for variable in keys],
                    having=[sql.call("COUNT", ["*"]) + " > 0"],
                )

            case _:
                return super().generate_primitive(label)

        return sql.cte(
            name=label.identifier,
            columns=[
                constants.Names.NOTHING,
                *(variable.identifier for variable in self.outputs_of[label]),
            ],
            body=body,
        )
