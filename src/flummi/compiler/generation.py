from dataclasses import dataclass, field

from ..IR.CFP import (
    Assignment,
    Emit,
    Fork,
    Gather,
    GoTo,
    Label,
    Merge,
    Primitive,
    Program,
    Start,
    Where,
    IsSynced,
)
from ..library import graph, sql
from .allocation import AllocationResult
from .analysis import AnalysisResult, Feature
from .names import Names, SystemVariable
from .solving import DataflowResult

__all__ = ("generate",)


def generate(
    program: Program,
    analysis: AnalysisResult,
    dataflow: DataflowResult,
    allocation: AllocationResult,
) -> str:
    return CodeGenerator(
        dataflow,
        allocation,
        analysis,
    ).gen_program(program)


@dataclass
class CodeGenerator:
    _dataflow: DataflowResult
    _allocation: AllocationResult
    _analysis: AnalysisResult

    _linear: bool = field(init=False)

    def __post_init__(self):
        self._linear = Feature.ITERATING not in self._analysis.features

    def gen_program(self, program: Program) -> sql.SQL:
        if self._linear:
            return self.gen_linear_program(program)
        else:
            return self.gen_nonlinear_program(program)

    def gen_linear_program(self, program: Program) -> sql.SQL:
        cfp = program.body
        predecessors_of = graph.invert(cfp.successors_of)

        assert self._linear and all(
            not isinstance(primitive, GoTo) for primitive in cfp.primitives
        )

        ctes = [
            self.gen_primitive(
                cfp.primitives[label],
                predecessors_of[label],
                label,
            )
            for label in graph.topological_order(cfp.successors_of)
        ]

        collectors = [
            sql.select(
                select_list=[
                    sql.variable(SystemVariable.RESULT, label.identifier)
                ],
                from_list=[sql.name(label.identifier)],
            )
            for label, primitive in cfp.primitives.items()
            if isinstance(primitive, Emit)
        ]

        return sql.with_ctes(ctes=ctes, body=sql.union_all(collectors))

    def gen_nonlinear_program(self, program: Program) -> sql.SQL:
        cfp = program.body
        predecessors_of = graph.invert(cfp.successors_of)

        ctes: list[sql.SQL] = []
        collectors: list[sql.SQL] = []
        for label in graph.topological_order(cfp.successors_of):
            primitive = cfp.primitives[label]

            ctes.append(
                self.gen_primitive(
                    cfp.primitives[label],
                    predecessors_of[label],
                    label,
                )
            )

            match primitive:
                case GoTo(target_label):
                    collectors.append(
                        sql.select(
                            select_list=[
                                sql.named(
                                    sql.cast(
                                        (
                                            sql.variable(
                                                SystemVariable.ITERATION,
                                                label.identifier,
                                            )
                                            + " + 1"
                                            if column
                                            == SystemVariable.ITERATION
                                            else sql.NULL
                                            if (
                                                variable := self._allocation.at[
                                                    target_label
                                                ].variable_at(column)
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
                                for column, type in self._allocation.schema.items()
                            ],
                            from_list=[sql.name(label.identifier)],
                        )
                    )

                case Emit(_):
                    collectors.append(
                        sql.select(
                            select_list=[
                                sql.named(
                                    sql.cast(
                                        (
                                            sql.variable(
                                                column,
                                                label.identifier,
                                            )
                                            if column
                                            in {
                                                SystemVariable.RESULT,
                                                SystemVariable.ITERATION,
                                            }
                                            else sql.NULL
                                        ),
                                        type.source,
                                    ),
                                    column,
                                )
                                for column, type in self._allocation.schema.items()
                            ],
                            from_list=[sql.name(label.identifier)],
                        )
                    )

                case _:
                    ...

        recursive_anchor = sql.with_ctes(
            ctes=ctes, body=sql.union_all(collectors)
        )

        base_anchor = sql.select(
            select_list=[
                sql.named(
                    sql.cast(
                        (
                            sql.string(program.body.entry_label.identifier)
                            if column == SystemVariable.LABEL
                            else "0"
                            if column == SystemVariable.ITERATION
                            else sql.NULL
                        ),
                        type.source,
                    ),
                    column,
                )
                for column, type in self._allocation.schema.items()
            ]
        )

        recursive_cte = sql.cte(
            name=Names.LOOP,
            columns=list(self._allocation.schema),
            body=sql.union_all([base_anchor, recursive_anchor]),
        )

        result_selection = sql.select(
            select_list=[sql.variable(SystemVariable.RESULT, Names.LOOP)],
            from_list=[sql.name(Names.LOOP)],
            predicates=[
                sql.variable(SystemVariable.LABEL, Names.LOOP) + " IS NULL"
            ],
        )

        return (
            sql.with_ctes(
                ctes=[recursive_cte], recursive=True, body=result_selection
            )
            + ";"
        )

    def gen_primitive(
        self,
        primitive: Primitive,
        predecessors: set[Label],
        label: Label,
    ) -> sql.SQL:
        match primitive:
            case Start() if self._linear:
                assert len(predecessors) == 0

                body = sql.select(
                    select_list=[
                        sql.named(
                            "0"
                            if output.identifier == SystemVariable.ITERATION
                            else sql.NULL,
                            output.identifier,
                        )
                        for output in self._dataflow.outputs_of[label]
                    ],
                )

            case Start() if not self._linear:
                assert len(predecessors) == 0

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.variable(
                                SystemVariable.ITERATION,
                                Names.LOOP,
                            )
                            if output.identifier == SystemVariable.ITERATION
                            else sql.variable(
                                column,
                                Names.LOOP,
                            )
                            if (
                                column := self._allocation.at[label].column_for(
                                    output
                                )
                            )
                            else sql.NULL,
                            output.identifier,
                        )
                        for output in self._dataflow.outputs_of[label]
                    ],
                    from_list=[sql.name(Names.LOOP)],
                    predicates=[
                        sql.variable(SystemVariable.LABEL, Names.LOOP)
                        + " IS NOT DISTINCT FROM "
                        + sql.string(label.identifier)
                    ],
                )

            case Assignment(variable, expression):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.cast(
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
                                ),
                                self._analysis.symbol_table[variable].source,
                            )
                            if output == variable
                            else sql.variable(
                                output.identifier, predecessor.identifier
                            ),
                            output.identifier,
                        )
                        for output in self._dataflow.outputs_of[label]
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                )

            case Emit(variable):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.variable(
                                variable.identifier, predecessor.identifier
                            )
                            if output.identifier == SystemVariable.RESULT
                            else sql.variable(
                                output.identifier, predecessor.identifier
                            ),
                            output.identifier,
                        )
                        for output in self._dataflow.outputs_of[label]
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                )

            case Where(condition, inverted):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.variable(
                                output.identifier, predecessor.identifier
                            ),
                            output.identifier,
                        )
                        for output in self._dataflow.outputs_of[label]
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                    predicates=[
                        f"{sql.variable(condition.identifier, predecessor.identifier)} "
                        + f"IS {'NOT ' * (not inverted)}"
                        + "DISTINCT FROM TRUE"
                    ],
                )

            case Merge():
                body = sql.union_all(
                    [
                        sql.select(
                            select_list=[
                                sql.named(
                                    sql.variable(
                                        output.identifier,
                                        predecessor.identifier,
                                    ),
                                    output.identifier,
                                )
                                for output in self._dataflow.outputs_of[label]
                            ],
                            from_list=[sql.name(predecessor.identifier)],
                        )
                        for predecessor in predecessors
                    ]
                )

            case GoTo(target_label):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.string(target_label.identifier)
                            if output.identifier == SystemVariable.LABEL
                            else sql.variable(
                                output.identifier, predecessor.identifier
                            ),
                            output.identifier,
                        )
                        for output in self._dataflow.outputs_of[label]
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                )

            case Fork(variables, expression):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                body = sql.select(
                    select_list=[
                        *(
                            sql.named(
                                sql.variable(
                                    output.identifier,
                                    Names.EXPRESSION,
                                )
                                if output in variables
                                else sql.variable(
                                    output.identifier, predecessor.identifier
                                ),
                                output.identifier,
                            )
                            for output in self._dataflow.outputs_of[label]
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
                            Names.EXPRESSION,
                            [variable.identifier for variable in variables],
                        ),
                    ],
                )

            case Gather(aggregates, keys):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                keys.append(
                    self._analysis.system_variables[SystemVariable.CONTROL]
                )

                body = sql.select(
                    select_list=[
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
                            for output in self._dataflow.outputs_of[label]
                        ),
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                    group_keys=[
                        sql.variable(
                            variable.identifier,
                            predecessor.identifier,
                        )
                        for variable in keys
                    ],
                    having=[sql.call("COUNT", ["*"]) + " > 0"],
                )

            case IsSynced(variable, sync_label, keys):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                body = sql.select(
                    select_list=[
                        *(
                            sql.named(
                                (
                                    sql.call(
                                        "NOT EXISTS ",
                                        [
                                            sql.paren(
                                                sql.select(
                                                    select_list=[
                                                        sql.NULL,
                                                    ],
                                                    from_list=[
                                                        sql.name(Names.LOOP)
                                                    ],
                                                    predicates=[
                                                        sql.variable(
                                                            SystemVariable.LABEL,
                                                            Names.LOOP,
                                                        )
                                                        + " <> "
                                                        + sql.string(
                                                            sync_label.identifier
                                                        ),
                                                        *(
                                                            sql.variable(
                                                                column,
                                                                Names.LOOP,
                                                            )
                                                            + " = "
                                                            + sql.variable(
                                                                key.identifier,
                                                                predecessor.identifier,
                                                            )
                                                            for key in keys
                                                            if (
                                                                column
                                                                := self._allocation.at[
                                                                    sync_label
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
                            for output in self._dataflow.outputs_of[label]
                        ),
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                )

            case _:
                raise NotImplementedError()

        cte = sql.cte(
            name=label.identifier,
            columns=[
                output.identifier for output in self._dataflow.outputs_of[label]
            ],
            body=body,
        )

        return cte
