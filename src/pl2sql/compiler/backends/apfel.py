from typing import override

from .base import GenerationError
from .lateral import LateralGenerator
from .. import constants
from ..features import Feature
from ...IR import CFP
from ...library import sql, graph


class ApfelGenerator(
    LateralGenerator,
    name="apfel",
    supports={Feature.SEQUENCING, Feature.BRANCHING},
):
    @override
    def generate(self) -> sql.SQL:
        start_candidates = [
            label
            for label, primitive in self.program.body.primitives.items()
            if isinstance(primitive, CFP.Start)
        ]

        if len(start_candidates) != 1:
            raise GenerationError(
                f"This generator only support exactly one start node, your program contains {len(start_candidates)}.",
            )

        return self.generate_region(start_candidates[0]) + ";"

    def generate_region(self, entry_label: CFP.Label) -> sql.SQL:
        region_labels = self.guarded_by[entry_label]
        region = graph.subgraph(self.program.body.edges, region_labels)
        predecessors = graph.invert(self.program.body.edges)

        from_list: list[sql.SQL] = []
        results: list[sql.SQL] = []

        for label in graph.topological_order(region):
            primitive = self.program.body.primitives[label]
            match primitive:
                case CFP.Where(variable) | CFP.WhereNot(variable):
                    assert len(predecessors[label]) == 1
                    predecessor = list(predecessors[label])[0]

                    child_region = self.generate_region(label)

                    results.append(
                        sql.select(
                            [
                                sql.variable(
                                    constants.Names.RESULT,
                                    label.identifier,
                                )
                            ],
                            [
                                sql.named(
                                    sql.paren(child_region),
                                    label.identifier,
                                    columns=[constants.Names.RESULT],
                                )
                            ],
                            predicates=[
                                sql.variable(
                                    variable.identifier,
                                    self.definitions_after[predecessor][
                                        variable
                                    ].identifier,
                                )
                                + " IS NOT DISTINCT FROM "
                                + (
                                    "TRUE"
                                    if isinstance(primitive, CFP.Where)
                                    else "FALSE"
                                )
                            ],
                        )
                    )

                case CFP.Emit(variable):
                    assert len(predecessors[label]) == 1
                    predecessor = list(predecessors[label])[0]

                    results.append(
                        sql.select(
                            [
                                sql.named(
                                    sql.variable(
                                        variable.identifier,
                                        self.definitions_after[predecessor][
                                            variable
                                        ].identifier,
                                    ),
                                    label.identifier + constants.Names.RESULT,
                                )
                            ]
                        )
                    )

                case _:
                    if results:
                        raise GenerationError(
                            "Found non-exiting primitive between exiting ones!"
                        )

                    from_list.append(
                        self.generate_primitive(
                            label, primitive, predecessors[label]
                        )
                    )

        from_list.append(
            sql.named(
                sql.lateral(sql.union_all(results)),
                constants.Names.RESULT,
                columns=[constants.Names.RESULT],
            )
        )

        return sql.select(
            select_list=[
                sql.variable(constants.Names.RESULT, constants.Names.RESULT)
            ],
            from_list=from_list,
        )
