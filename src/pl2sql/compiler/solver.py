from collections import defaultdict
from dataclasses import dataclass


from ..IR import CFP, common
from ..library import utils, graph, errors
from .analyzer import SymbolTable
from . import names

__all__ = ("solve",)


class SolverError(errors.PrettyError, ValueError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


@dataclass
class FlowSolution:
    inputs_of: dict[CFP.Label, set[common.Identifier]]
    outputs_of: dict[CFP.Label, set[common.Identifier]]

    binding_sites_after: dict[CFP.Label, dict[common.Identifier, CFP.Label]]
    guard_of: dict[CFP.Label, CFP.Label]
    guarded_by: dict[CFP.Label, set[CFP.Label]]


def solve(program: CFP.Program, symbol_table: SymbolTable) -> FlowSolution:
    return FlowSolver(symbol_table).solve_program(program)


@dataclass
class FlowSolver:
    symbol_table: SymbolTable

    def solve_program(self, program: CFP.Program) -> FlowSolution:
        cfp = program.body

        inputs_of, outputs_of = self.live_variable_analysis(cfp)

        binding_sites_after = self.reaching_definition_analysis(cfp)

        guard_of, guarded_by = self.guard_analysis(cfp)

        return FlowSolution(
            inputs_of, outputs_of, binding_sites_after, guard_of, guarded_by
        )

    @staticmethod
    def live_variable_analysis(
        cfp: CFP.Graph,
    ) -> tuple[
        dict[CFP.Label, set[common.Identifier]],
        dict[CFP.Label, set[common.Identifier]],
    ]:
        inputs_of = {
            label: FlowSolver.uses(primitive)
            for label, primitive in cfp.primitives.items()
        }
        outputs_of = {
            label: FlowSolver.binds(primitive)
            for label, primitive in cfp.primitives.items()
        }

        predecessors_of = graph.invert(cfp.transitions)

        worklist = set(cfp.primitives)

        while worklist:
            label = worklist.pop()

            new_outputs = (
                utils.union(
                    inputs_of[successor] for successor in cfp.transitions[label]
                )
                - outputs_of[label]
            )

            if not new_outputs:
                continue

            inputs_of[label] |= new_outputs
            outputs_of[label] |= new_outputs

            worklist |= predecessors_of[label]

        return inputs_of, outputs_of

    @staticmethod
    def uses(primitive: CFP.Primitive) -> set[common.Identifier]:
        match primitive:
            case CFP.Let(_, common.Expression(_, variables)):
                return set(variables)

            case (
                CFP.Emit(variable)
                | CFP.Where(variable)
                | CFP.WhereNot(variable)
            ):
                return {variable}

            case _:
                return set()

    @staticmethod
    def binds(primitive: CFP.Primitive) -> set[common.Identifier]:
        match primitive:
            case CFP.Start():
                return {
                    common.Identifier(
                        names.nothing, location=primitive.location
                    )
                }

            case CFP.Let(variable, _):
                return {variable}

            case CFP.Emit(_):
                return {
                    common.Identifier(names.result, location=primitive.location)
                }

            case _:
                return set()

    @staticmethod
    def reaching_definition_analysis(
        cfp: CFP.Graph,
    ) -> dict[CFP.Label, dict[common.Identifier, CFP.Label]]:
        predecessors_of = graph.invert(cfp.transitions)

        binding_sites_after: dict[
            CFP.Label, dict[common.Identifier, CFP.Label]
        ] = {}

        for label in graph.topological_order(cfp.transitions):
            primitive = cfp.primitives[label]

            binding_sites_after_here = dict[common.Identifier, CFP.Label]()

            if len(predecessors_of[label]) > 0:
                first_predecessor, *other_predecessors = predecessors_of[label]

                if isinstance(primitive, CFP.Merge):
                    variables_to_rebind = set(
                        binding_sites_after[first_predecessor]
                    )
                    for predecessor in other_predecessors:
                        # We only keep the variables that always have a garanteed
                        # associated binding in all of the predecessors.
                        variables_to_rebind &= binding_sites_after[
                            predecessor
                        ].keys()

                    binding_sites_after_here = {
                        variable: label for variable in variables_to_rebind
                    }
                else:
                    # For anything but merges, there should be only at most one
                    # predecessor.
                    assert not other_predecessors

                    # We need to explicitly copy here, otherwise all labels from
                    # here until the next merge will share the same dictionary
                    # object in memory...
                    binding_sites_after_here = dict(
                        binding_sites_after[first_predecessor]
                    )

            if isinstance(primitive, CFP.Let):
                binding_sites_after_here |= {primitive.variable: label}

            binding_sites_after[label] = binding_sites_after_here

        return binding_sites_after

    @staticmethod
    def guard_analysis(
        cfp: CFP.Graph,
    ) -> tuple[dict[CFP.Label, CFP.Label], dict[CFP.Label, set[CFP.Label]]]:
        GUARDING_PRIMITIVES: tuple[type[CFP.Primitive], ...] = (
            CFP.Start,
            CFP.Where,
            CFP.WhereNot,
            # Merges act as virtual guards, i.e., they do not introduce a "new"
            # guarded region for their successors, but act as a standin for
            # their (the merges) own guard and their region.
            CFP.Merge,
        )

        guard_of: dict[CFP.Label, CFP.Label] = {}

        levels: dict[CFP.Label, int] = {
            label: 0
            for label, primitive in cfp.primitives.items()
            if isinstance(primitive, CFP.Start)
        }

        for guard_label in graph.topological_order(cfp.transitions):
            guard_primitive = cfp.primitives[guard_label]
            if isinstance(guard_primitive, GUARDING_PRIMITIVES):
                stack: list[CFP.Label] = list(cfp.transitions[guard_label])
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
                                # A superceeding guard has already been found
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
                            stack.extend(cfp.transitions[label])

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
        # hassel and sacrafice of cleanliness since we can do it easily
        # afterwards, i.e., here.
        guarded_by: dict[CFP.Label, set[CFP.Label]] = defaultdict(set)
        for guardee, guard in guard_of.items():
            guarded_by[guard].add(guardee)

        return guard_of, guarded_by
