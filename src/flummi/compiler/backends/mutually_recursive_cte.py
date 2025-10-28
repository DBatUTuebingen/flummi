from typing import override

from .mixins import UseLiveVariables
from .cte import CTEBackend
from .. import constants
from ..features import Feature
from ...IR import CFP
from ...library import sql, graph, utils


class MutuallyRecursiveCTEBackend(
    CTEBackend,
    UseLiveVariables,
    name="mutually_recursive_cte",
    supports={Feature.SEQUENCING, Feature.BRANCHING, Feature.ITERATION},
):
    @override
    def generate(self) -> sql.SQL:
        ctes = [
            self.generate_primitive(label)
            for label in graph.topological_order(self.successors_of)
            if not isinstance(self.primitives[label], CFP.GoTo)
        ]

        return (
            sql.with_ctes(
                ctes=ctes,
                mutually_recursive=True,
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
                        for label, primitive in self.primitives.items()
                        if isinstance(primitive, CFP.Emit)
                    ]
                ),
            )
            + ";"
        )

    @override
    def generate_primitive(self, label: CFP.Label) -> sql.SQL:
        primitive = self.primitives[label]
        predecessors = self.predecessors_of[label]

        outputs = {
            variable.identifier: self.symbol_table[variable].source
            for variable in self.outputs_of[label]
        } or {constants.Names.NOTHING: "TEXT"}

        predecessors_of = graph.invert(self.program.body.direct_edges)

        match primitive:
            case CFP.Start() if label == self.program.body.entry_label:
                assert len(predecessors) == 0

                body = sql.select(
                    select_list=[
                        sql.named(sql.NULL, output) for output in outputs
                    ],
                )

            case CFP.Start():
                assert len(predecessors) == 0

                virtual_predecessors = utils.union(
                    predecessors_of[goto_label]
                    for goto_label, primitive in self.program.body.primitives.items()
                    if isinstance(primitive, CFP.GoTo)
                    and label == primitive.label
                )

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
                        for predecessor in virtual_predecessors
                    ]
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
                return super().generate_primitive(label)

        return sql.typed_cte(
            name=label.identifier,
            columns=outputs,
            body=body,
        )
