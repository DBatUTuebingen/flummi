from ...IR import CFP
from ...library import graph

__all__ = ("analyze_reaching_definitions",)


type Definitions = dict[CFP.Variable, CFP.Label]


def analyze_reaching_definitions(
    program: CFP.Program,
) -> dict[CFP.Label, Definitions]:
    cfp = program.body

    predecessors_of = graph.invert(cfp.edges)

    definitions_after: dict[CFP.Label, Definitions] = {}

    for label in graph.topological_order(cfp.edges):
        primitive = cfp.primitives[label]

        definitions_after_here: Definitions = {}

        if len(predecessors_of[label]) > 0:
            first_predecessor, *other_predecessors = predecessors_of[label]

            if isinstance(primitive, CFP.Merge):
                variables_to_redefine = set(
                    definitions_after[first_predecessor]
                )
                for predecessor in other_predecessors:
                    # We only keep the variables that always have a garanteed
                    # associated binding in all of the predecessors.
                    variables_to_redefine &= definitions_after[
                        predecessor
                    ].keys()

                definitions_after_here = {
                    variable: label for variable in variables_to_redefine
                }
            else:
                # For anything but merges, there should be only at most one
                # predecessor.
                assert not other_predecessors

                # We need to explicitly copy here, otherwise all labels from
                # here until the next merge will share the same dictionary
                # object in memory...
                definitions_after_here = dict(
                    definitions_after[first_predecessor]
                )

        if isinstance(primitive, CFP.Let):
            definitions_after_here |= {primitive.variable: label}

        definitions_after[label] = definitions_after_here

    return definitions_after
