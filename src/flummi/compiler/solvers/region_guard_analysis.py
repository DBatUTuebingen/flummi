from collections import defaultdict

from ...IR import CFP
from ...library import graph

__all__ = ("analyze_region_guards",)


type Guard = CFP.Label
type Region = set[CFP.Label]

type GuardMap = CFP.PerLabel[Guard]
type RegionMap = CFP.PerLabel[Region]


def analyze_region_guards(program: CFP.Program) -> tuple[GuardMap, RegionMap]:
    cfp = program.body

    # This implementation doesn't support cycles! Since we don't implement any
    # code generators for cyclic CFPs that use region/guard information, we
    # don't need a full-blown PST-style region analysis.
    assert not cfp.indirect_edges

    # Guarding primitives are those who control the control flow of their
    # successors, i.e., either control flow sourcse like starts or conditionals
    # like wheres and where nots.
    GUARDING_PRIMITIVES: tuple[type[CFP.Primitive], ...] = (
        CFP.Start,
        CFP.Where,
        CFP.WhereNot,
        # Merges act as virtual guards, i.e., they do not introduce a "new"
        # guarded region for their successors, but act as a standin for
        # their (the merges) own guard and their region.
        CFP.Merge,
    )

    guard_of: CFP.PerLabel[Guard] = {}

    levels: CFP.PerLabel[int] = {
        label: 0
        for label, primitive in cfp.primitives.items()
        if isinstance(primitive, CFP.Start)
    }

    # We iterate through the whole CFP by iterating over all guards in
    # topoligical order—this ensures that we visit all guards of other guards
    # before the guards they guard. :-)
    for guard_label in graph.topological_order(cfp.direct_edges):
        guard_primitive = cfp.primitives[guard_label]
        if isinstance(guard_primitive, GUARDING_PRIMITIVES):
            # For each guard, we collect all of its guardees using a simple
            # depth first traversal terminated by other guards.
            stack: list[CFP.Label] = list(cfp.direct_edges[guard_label])

            if isinstance(guard_primitive, CFP.Merge):
                # Since merges are control dependent on their predecessors
                # and the topological order garantees that all control
                # dependencies are visited before we get here, we can simply
                # lookup the merges guard and to use for this segement.
                guard_label = guard_of[guard_label]
            elif guard_label in guard_of:
                levels[guard_label] = levels[guard_of[guard_label]] + 1

            while stack:
                label = stack.pop()
                primitive = cfp.primitives[label]

                if isinstance(primitive, CFP.Merge):
                    guards_guard = guard_of[guard_label]
                    if existing_guard := guard_of.get(label):
                        if levels[guards_guard] > levels[existing_guard]:
                            # A superceding guard has already been found
                            # for this merge, so we don't need to do
                            # anything here.
                            continue

                    guard_of[label] = guards_guard
                else:
                    # For anything but merges, there should be no prior
                    # guard for the current label.
                    assert label not in guard_of

                    guard_of[label] = guard_label

                    if not isinstance(primitive, GUARDING_PRIMITIVES):
                        stack.extend(cfp.direct_edges[label])

    # Excluding the start primitives, all other primitives should have been
    # assigned a guard once the above loop(s) have been completed.
    assert guard_of.keys() == {
        label
        for label, primitive in cfp.primitives.items()
        if not isinstance(primitive, CFP.Start)
    }

    # We can only compute this afterwards instead of "on the fly" during the
    # loop(s) above, since merges can possibly be re-assigned from one guard
    # to another, depending on the order in which we visit the guards. The
    # necessary special casing to cover this re-assignment is not worth the
    # hassel and sacrifice of cleanliness since we can do it easily
    # afterwards, i.e., here.
    guarded_by: dict[Guard, Region] = defaultdict(set)
    for guardee, guard in guard_of.items():
        guarded_by[guard].add(guardee)

    return guard_of, guarded_by
