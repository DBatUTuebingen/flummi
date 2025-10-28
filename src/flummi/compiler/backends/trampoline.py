from dataclasses import dataclass, field
from typing import override, ClassVar

from .base import PrimitiveBackend
from .mixins import UseFullAllocation, UseLiveVariables
from .. import constants
from ..features import Feature
from ...IR import CFP
from ...library import sql


type BranchIndex = int


@dataclass
class TrampolineBackend(
    PrimitiveBackend,
    UseFullAllocation,
    UseLiveVariables,
    name="trampoline",
    supports={Feature.SEQUENCING, Feature.BRANCHING, Feature.ITERATION},
):
    branch_index_of: dict[CFP.Label, BranchIndex] = field(init=False)
    OUTPUT_BRANCH_INDEX: ClassVar[BranchIndex] = 0

    def __post_init__(self):
        super().__post_init__()

        self.branch_index_of = {}

        for label, successors in self.virtual_successors_of.items():
            if successors or isinstance(self.primitives[label], CFP.Emit):
                self.branch_index_of[label] = 1 + len(self.branch_index_of)

    @override
    def generate(self) -> sql.SQL:
        branches = [
            sql.select(
                select_list=[
                    sql.named(
                        sql.cast(
                            sql.NULL
                            if column != constants.Names.LABEL
                            else str(
                                self.branch_index_of[
                                    self.program.body.entry_label
                                ]
                            ),
                            type.source
                            if column != constants.Names.LABEL
                            else "INT",
                        ),
                        column,
                    )
                    for column, type in self.schema.items()
                ]
            )
        ] + [self.generate_primitive(label) for label in self.branch_index_of]

        return (
            sql.select(
                select_list=[
                    sql.variable(
                        constants.Names.RESULT, constants.Names.WORKING_TABLE
                    )
                ],
                from_list=[
                    sql.named(
                        sql.call(
                            "umbra.trampoline",
                            [
                                sql.call("TABLE ", [branch])
                                for branch in branches
                            ],
                        ),
                        constants.Names.WORKING_TABLE,
                        list(self.schema),
                    )
                ],
            )
            + ";"
        )

    @override
    def generate_primitive(
        self,
        label: CFP.Label,
    ) -> sql.SQL:
        outputs = self.outputs_of[label]
        primitive = self.primitives[label]
        allocation = self.allocation_for[label]
        successors: set[CFP.Label | None] = (
            self.virtual_successors_of[label] & self.branch_index_of.keys()
        )  # pyright: ignore[reportAssignmentType]

        match primitive:
            case CFP.Start():
                cte_body = sql.select(
                    select_list=[sql.named(sql.NULL, constants.Names.NOTHING)]
                    + [
                        sql.named(
                            sql.variable(column, constants.Names.TRAMPOLINE)
                            if (column := allocation.column_for(output))
                            is not None
                            else sql.NULL,
                            output.identifier,
                        )
                        for output in outputs
                    ],
                    from_list=[
                        sql.name(constants.Names.TRAMPOLINE),
                    ],
                )

            case CFP.Let(variable, expression):
                cte_body = sql.select(
                    select_list=[sql.named(sql.NULL, constants.Names.NOTHING)]
                    + [
                        sql.named(
                            expression.source.format(
                                *(
                                    sql.paren(
                                        sql.variable(
                                            column,
                                            constants.Names.TRAMPOLINE,
                                        )
                                    )
                                    if (
                                        column := allocation.column_for(
                                            argument
                                        )
                                    )
                                    is not None
                                    else sql.NULL
                                    for argument in expression.arguments
                                )
                            )
                            if output == variable
                            else sql.variable(
                                column, constants.Names.TRAMPOLINE
                            )
                            if (column := allocation.column_for(output))
                            is not None
                            else sql.NULL,
                            output.identifier,
                        )
                        for output in outputs
                    ],
                    from_list=[
                        sql.name(constants.Names.TRAMPOLINE),
                    ],
                )

            case CFP.Emit(variable):
                cte_body = sql.select(
                    select_list=[sql.named(sql.NULL, constants.Names.NOTHING)]
                    + [
                        sql.named(
                            (
                                sql.variable(
                                    _column,
                                    constants.Names.TRAMPOLINE,
                                )
                                if (_column := allocation.column_for(variable))
                                is not None
                                else sql.NULL
                            )
                            if output.identifier == constants.Names.RESULT
                            else sql.NULL,
                            output.identifier,
                        )
                        for output in outputs
                    ],
                    from_list=[
                        sql.name(constants.Names.TRAMPOLINE),
                    ],
                )
                successors.add(None)

            case CFP.Where(variable) | CFP.WhereNot(variable):
                cte_body = sql.select(
                    select_list=[sql.named(sql.NULL, constants.Names.NOTHING)]
                    + [
                        sql.named(
                            sql.variable(column, constants.Names.TRAMPOLINE)
                            if (column := allocation.column_for(output))
                            is not None
                            else sql.NULL,
                            output.identifier,
                        )
                        for output in outputs
                    ],
                    from_list=[
                        sql.name(constants.Names.TRAMPOLINE),
                    ],
                    predicates=[
                        (
                            sql.variable(column, constants.Names.TRAMPOLINE)
                            if (column := allocation.column_for(variable))
                            is not None
                            else sql.NULL
                        )
                        + " IS NOT DISTINCT FROM "
                        + (
                            "TRUE"
                            if isinstance(primitive, CFP.Where)
                            else "FALSE"
                        )
                    ],
                )

            case CFP.Merge() | CFP.GoTo(_):
                cte_body = sql.select(
                    select_list=[sql.named(sql.NULL, constants.Names.NOTHING)]
                    + [
                        sql.named(
                            sql.variable(column, constants.Names.TRAMPOLINE)
                            if (column := allocation.column_for(output))
                            is not None
                            else sql.NULL,
                            output.identifier,
                        )
                        for output in outputs
                    ],
                    from_list=[
                        sql.name(constants.Names.TRAMPOLINE),
                    ],
                )

            case _:
                return super().generate_primitive(label)

        cte = sql.cte(
            name=constants.Names.BODY,
            columns=[
                constants.Names.NOTHING,
                *(output.identifier for output in outputs),
            ],
            body=cte_body,
        )

        dispatch_query = sql.union_all(
            [
                sql.select(
                    select_list=[
                        sql.named(
                            sql.cast(
                                (
                                    str(self.branch_index_of[successor])
                                    if column == constants.Names.LABEL
                                    else sql.variable(
                                        variable.identifier,
                                        constants.Names.BODY,
                                    )
                                    if (
                                        variable := self.allocation_for[
                                            successor
                                        ].variable_at(column)
                                    )
                                    is not None
                                    else sql.NULL
                                )
                                if successor is not None
                                else (
                                    str(self.OUTPUT_BRANCH_INDEX)
                                    if column == constants.Names.LABEL
                                    else sql.variable(
                                        constants.Names.RESULT,
                                        constants.Names.BODY,
                                    )
                                    if column == constants.Names.RESULT
                                    else sql.NULL
                                ),
                                type.source
                                if column != constants.Names.LABEL
                                else "INT",
                            ),
                            column,
                        )
                        for column, type in self.schema.items()
                    ],
                    from_list=[sql.name(constants.Names.BODY)],
                )
                for successor in successors
            ]
        )

        return sql.with_ctes([cte], dispatch_query)
