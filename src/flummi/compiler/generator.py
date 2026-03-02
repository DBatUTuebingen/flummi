from dataclasses import dataclass

from . import names
from .solver import Dataflow
from ..IR import CFP
from ..library import sql, graph


__all__ = ("generate",)


def generate(program: CFP.Program, dataflow: Dataflow) -> str:
    return CodeGenerator(dataflow).gen_program(program)


@dataclass
class CodeGenerator:
    dataflow: Dataflow

    def gen_program(self, program: CFP.Program) -> sql.SQL:
        cfp = program.body
        predecessors = graph.invert(cfp.transitions)

        ctes = [
            self.gen_primitive(
                cfp.primitives[label], predecessors[label], label
            )
            for label in graph.topological_order(cfp.transitions)
        ]

        return sql.with_ctes(
            ctes=ctes,
            body=sql.union_all(
                [
                    sql.select(
                        select_list=[
                            sql.variable(names.result, label.identifier)
                        ],
                        from_list=[sql.name(label.identifier)],
                    )
                    for label, primitive in cfp.primitives.items()
                    if isinstance(primitive, CFP.Emit)
                ]
            ),
        )

    def gen_primitive(
        self,
        primitive: CFP.Primitive,
        predecessors: set[CFP.Label],
        label: CFP.Label,
    ) -> sql.SQL:
        match primitive:
            case CFP.Start():
                assert len(predecessors) == 0

                body = sql.select(
                    select_list=[
                        sql.named(
                            "NULL",
                            output.identifier,
                        )
                        for output in self.dataflow.outputs[label]
                    ],
                )

            case CFP.Assignment(variable, expression):
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
                            if output == variable
                            else sql.variable(
                                output.identifier, predecessor.identifier
                            ),
                            output.identifier,
                        )
                        for output in self.dataflow.outputs[label]
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
                            if output.identifier == names.result
                            else sql.variable(
                                output.identifier, predecessor.identifier
                            ),
                            output.identifier,
                        )
                        for output in self.dataflow.outputs[label]
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                )

            case CFP.Where(condition, inverted):
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
                        for output in self.dataflow.outputs[label]
                    ],
                    from_list=[sql.name(predecessor.identifier)],
                    predicates=[
                        f"{sql.variable(condition.identifier, predecessor.identifier)} "
                        + f"IS {'NOT ' * (not inverted)}"
                        + "DISTINCT FROM TRUE"
                    ],
                )

            case CFP.Merge():
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
                                for output in self.dataflow.outputs[label]
                            ],
                            from_list=[sql.name(predecessor.identifier)],
                        )
                        for predecessor in predecessors
                    ]
                )

            case _:
                raise NotImplementedError()

        return sql.cte(
            name=label.identifier,
            columns=[
                output.identifier for output in self.dataflow.outputs[label]
            ],
            body=body,
        )
