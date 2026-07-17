from dataclasses import dataclass, field

from ..IR.CFP import (
    Assignment,
    Emit,
    Fork,
    Gather,
    IsSynced,
    Jump,
    Label,
    Merge,
    Primitive,
    Program,
    Start,
    Stop,
    Where,
)
from ..library import graph, sql
from .analysis import AnalysisResult, Feature
from .names import Names, SystemVariable
from .scheming import Schema
from .solving import DataflowResult

__all__ = ("generate",)


def generate(
    program: Program,
    analysis: AnalysisResult,
    dataflow: DataflowResult,
    schema: Schema,
) -> str:
    return CodeGenerator(
        dataflow,
        schema,
        analysis,
    ).gen_program(program)


@dataclass
class CodeGenerator:
    _dataflow: DataflowResult
    _schema: Schema
    _analysis: AnalysisResult

    _linear: bool = field(init=False)
    _result_columns: tuple[str, ...] = field(init=False)
    _column_order: dict[str, tuple[int, int, str]] = field(init=False)

    def __post_init__(self):
        self._linear = Feature.ITERATING not in self._analysis.features
        self._result_columns = tuple(
            variable.identifier for variable in self._analysis.result_variables
        )
        self._column_order = {}

        for index, column in enumerate(
            (
                SystemVariable.ITERATION,
                SystemVariable.LABEL,
                SystemVariable.CONTROL,
                SystemVariable.PROBE,
            )
        ):
            self._column_order[column] = (0, index, column)

        for index, column in enumerate(self._result_columns):
            self._column_order[column] = (1, index, column)

        system_columns = {
            variable.identifier
            for variable in self._analysis.system_variables.values()
        }
        for variable in self._analysis.symbol_table:
            column = variable.identifier
            if (
                column not in system_columns
                and column not in self._column_order
            ):
                self._column_order[column] = (
                    2,
                    len(self._column_order),
                    column,
                )

        self._schema = {
            column: self._schema[column]
            for column in sorted(self._schema, key=self._column_key)
        }

    def _column_key(self, column: str) -> tuple[int, int, str]:
        return self._column_order.get(column, (3, 0, column))

    def gen_program(self, program: Program) -> sql.SQL:
        if self._linear:
            return self.gen_linear_program(program)
        else:
            return self.gen_nonlinear_program(program)

    def gen_linear_program(self, program: Program) -> sql.SQL:
        cfp = program.body
        predecessors_of = graph.invert(cfp.successors_of)

        assert self._linear and all(
            not isinstance(primitive, Jump) for primitive in cfp.primitives
        )

        ctes = [
            self.gen_primitive(
                cfp.primitives[label],
                predecessors_of[label],
                label,
            )
            for label in graph.topological_order(
                cfp.successors_of,
                key=lambda label: label.identifier,
            )
        ]

        collectors = [
            sql.select(
                select_list=[
                    sql.variable(column, label.identifier)
                    for column in self._result_columns
                ],
                from_list=[sql.name(label.identifier)],
            )
            for label, primitive in sorted(
                cfp.primitives.items(), key=lambda item: item[0].identifier
            )
            if isinstance(primitive, Emit)
        ]

        return sql.with_ctes(ctes=ctes, body=sql.union_all(collectors))

    def gen_nonlinear_program(self, program: Program) -> sql.SQL:
        cfp = program.body
        predecessors_of = graph.invert(cfp.successors_of)

        ctes: list[sql.SQL] = []
        collectors: list[sql.SQL] = []
        for label in graph.topological_order(
            cfp.successors_of,
            key=lambda label: label.identifier,
        ):
            primitive = cfp.primitives[label]

            ctes.append(
                self.gen_primitive(
                    cfp.primitives[label],
                    predecessors_of[label],
                    label,
                )
            )

            match primitive:
                case Jump():
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
                                            if column in self._result_columns
                                            else sql.variable(
                                                column,
                                                label.identifier,
                                            )
                                        ),
                                        type.source,
                                    ),
                                    column,
                                )
                                for column, type in self._schema.items()
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
                                            == SystemVariable.ITERATION
                                            or column in self._result_columns
                                            else sql.NULL
                                        ),
                                        type.source,
                                    ),
                                    column,
                                )
                                for column, type in self._schema.items()
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
                for column, type in self._schema.items()
            ]
        )

        recursive_cte = sql.cte(
            name=Names.LOOP,
            columns=list(self._schema),
            body=sql.union_all([base_anchor, recursive_anchor]),
        )

        result_selection = sql.select(
            select_list=[
                sql.variable(column, Names.LOOP)
                for column in self._result_columns
            ],
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
        outputs = sorted(
            self._dataflow.outputs_of[label],
            key=lambda variable: self._column_key(variable.identifier),
        )
        cte_columns = [variable.identifier for variable in outputs]

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
                        for output in outputs
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
                            else sql.NULL
                            if output.identifier == SystemVariable.CONTROL
                            else sql.variable(
                                output.identifier,
                                Names.LOOP,
                            ),
                            output.identifier,
                        )
                        for output in outputs
                    ],
                    from_list=[sql.name(Names.LOOP)],
                    predicates=[
                        sql.variable(SystemVariable.LABEL, Names.LOOP)
                        + " IS NOT DISTINCT FROM "
                        + sql.string(label.identifier)
                    ],
                )

            case Stop():
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                cte_columns = [SystemVariable.CONTROL.value]

                body = sql.select(
                    select_list=[
                        sql.variable(
                            SystemVariable.CONTROL, predecessor.identifier
                        )
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                    predicates=["FALSE"],
                )

            case Assignment(bindings):
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
                                self._analysis.symbol_table[output].source,
                            )
                            if (expression := bindings.get(output)) is not None
                            else sql.variable(
                                output.identifier, predecessor.identifier
                            ),
                            output.identifier,
                        )
                        for output in outputs
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                )

            case Emit(variables):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]
                result_bindings = dict(
                    zip(
                        self._analysis.result_variables,
                        variables,
                        strict=True,
                    )
                )

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.variable(
                                result_bindings[output].identifier,
                                predecessor.identifier,
                            )
                            if output in result_bindings
                            else sql.variable(
                                output.identifier, predecessor.identifier
                            ),
                            output.identifier,
                        )
                        for output in outputs
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
                        for output in outputs
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
                                for output in outputs
                            ],
                            from_list=[sql.name(predecessor.identifier)],
                        )
                        for predecessor in sorted(
                            predecessors, key=lambda label: label.identifier
                        )
                    ]
                )

            case Jump(target_label):
                assert len(predecessors) == 1
                predecessor = list(predecessors)[0]

                cte_columns = [
                    column
                    for column in self._schema
                    if column not in self._result_columns
                ]
                _outputs = {variable.identifier for variable in outputs}

                body = sql.select(
                    select_list=[
                        sql.named(
                            sql.string(target_label.identifier)
                            if output == SystemVariable.LABEL
                            else sql.variable(output, predecessor.identifier)
                            if output in _outputs
                            else sql.NULL,
                            output,
                        )
                        for output in cte_columns
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
                                sql.cast(
                                    sql.variable(
                                        output.identifier,
                                        Names.EXPRESSION,
                                    ),
                                    self._analysis.symbol_table[output].source,
                                )
                                if output in variables
                                else sql.variable(
                                    output.identifier, predecessor.identifier
                                ),
                                output.identifier,
                            )
                            for output in outputs
                        ),
                    ],
                    from_list=[
                        sql.name(predecessor.identifier),
                        sql.named(
                            (
                                sql.lateral
                                if expression.arguments
                                else sql.paren
                            )(
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

                keys.update(outputs - aggregates.keys())

                body = sql.select(
                    select_list=[
                        *(
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
                                    self._analysis.symbol_table[output].source,
                                )
                                if (expression := aggregates.get(output))
                                is not None
                                else sql.variable(
                                    output.identifier,
                                    predecessor.identifier,
                                ),
                                output.identifier,
                            )
                            for output in outputs
                        ),
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                    group_keys=[
                        sql.variable(
                            variable.identifier,
                            predecessor.identifier,
                        )
                        for variable in sorted(
                            keys, key=lambda variable: variable.identifier
                        )
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
                                                                key.identifier,
                                                                Names.LOOP,
                                                            )
                                                            + " = "
                                                            + sql.variable(
                                                                key.identifier,
                                                                predecessor.identifier,
                                                            )
                                                            for key in sorted(
                                                                keys,
                                                                key=lambda key: (
                                                                    key.identifier
                                                                ),
                                                            )
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
                            for output in outputs
                        ),
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                )

            case _:
                raise NotImplementedError()

        cte = sql.cte(
            name=label.identifier,
            columns=cte_columns,
            body=body,
        )

        return cte
