from dataclasses import dataclass

from ..IR import CFP, common
from ..library import utils, graph, errors
from . import names

__all__ = ("solve",)


class SolverError(errors.PrettyError, ValueError): ...  # pyright: ignore[reportUnsafeMultipleInheritance]


@dataclass
class Dataflow:
    inputs: dict[CFP.Label, set[common.Identifier]]
    outputs: dict[CFP.Label, set[common.Identifier]]

    binding_sites_at: dict[CFP.Label, dict[common.Identifier, CFP.Label]]
    guards: dict[CFP.Label, CFP.Label]


def solve(program: CFP.Program) -> Dataflow:
    return DataflowSolver().solve_program(program)


@dataclass
class DataflowSolver:
    def solve_program(self, program: CFP.Program) -> Dataflow:
        cfp = program.body

        inputs, outputs = self.live_variable_analysis(cfp)

        binding_sites_at = self.collect_binding_sites_at(cfp)

        guards = self.collect_guards(cfp)

        return Dataflow(inputs, outputs, binding_sites_at, guards)

    @staticmethod
    def live_variable_analysis(
        cfp: CFP.Graph,
    ) -> tuple[
        dict[CFP.Label, set[common.Identifier]],
        dict[CFP.Label, set[common.Identifier]],
    ]:
        inputs = {
            label: DataflowSolver.uses(primitive)
            for label, primitive in cfp.primitives.items()
        }
        outputs = {
            label: DataflowSolver.binds(primitive)
            for label, primitive in cfp.primitives.items()
        }

        changed = True
        while changed:
            changed = False
            for label in cfp.primitives:
                new_outputs = utils.union(
                    inputs[successor] for successor in cfp.transitions[label]
                )

                new_outputs -= outputs[label]

                if not new_outputs:
                    continue

                changed = True
                inputs[label] |= new_outputs
                outputs[label] |= new_outputs

        return inputs, outputs

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
    def collect_binding_sites_at(
        cfp: CFP.Graph,
    ) -> dict[CFP.Label, dict[common.Identifier, CFP.Label]]:
        predecessors = graph.invert(cfp.transitions)

        binding_sites_at: dict[
            CFP.Label, dict[common.Identifier, CFP.Label]
        ] = {}
        for label in graph.topological_order(cfp.transitions):
            primitive = cfp.primitives[label]

            binding_sites_after_here: dict[common.Identifier, CFP.Label] = {}

            if len(predecessors[label]) > 0:
                first_predecessor, *other_predecessors = predecessors[label]

                if isinstance(primitive, CFP.Merge):
                    variables_to_rebind = set(
                        binding_sites_at[first_predecessor]
                    )
                    for predecessor in other_predecessors:
                        # We only keep the variables that always have a garanteed
                        # associated binding in all of the predecessors.
                        variables_to_rebind &= binding_sites_at[
                            predecessor
                        ].keys()

                    binding_sites_after_here = {
                        variable: label for variable in variables_to_rebind
                    }
                else:
                    if other_predecessors:
                        raise SolverError(
                            "Found too many predecessors during binding compuation at...",
                            primitive.location,
                        )

                    # We need to explicitly copy here, otherwise all labels from
                    # here until the next merge will share the same dictionary
                    # object in memory...
                    binding_sites_after_here = dict(
                        binding_sites_at[first_predecessor]
                    )

            if isinstance(primitive, CFP.Let):
                binding_sites_after_here[primitive.variable] = label

            binding_sites_at[label] = binding_sites_after_here

        return binding_sites_at

    @staticmethod
    def collect_guards(cfp: CFP.Graph) -> dict[CFP.Label, CFP.Label]:
        GUARDING_PRIMITIVES: tuple[type[CFP.Primitive], ...] = (
            CFP.Start,
            CFP.Where,
            CFP.WhereNot,
            CFP.Merge,
        )

        guards: dict[CFP.Label, CFP.Label] = {}
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
                    guard_label = guards[guard_label]
                elif guard_label in guards:
                    levels[guard_label] = levels[guards[guard_label]] + 1

                while stack:
                    guarded_label = stack.pop(0)
                    guarded_primitive = cfp.primitives[guarded_label]

                    if isinstance(guarded_primitive, CFP.Merge):
                        guards_guard = guards[guard_label]
                        if existing_guard := guards.get(guarded_label):
                            if levels[guards_guard] > levels[existing_guard]:
                                continue
                        guards[guarded_label] = guards_guard
                    else:
                        if guarded_label in guards:
                            raise SolverError(
                                "Found multiple guards for primitive at...",
                                guarded_primitive.location,
                            )

                        guards[guarded_label] = guard_label

                        if not isinstance(
                            guarded_primitive, GUARDING_PRIMITIVES
                        ):
                            stack.extend(cfp.transitions[guarded_label])

        if guards.keys() != {
            label
            for label, primitive in cfp.primitives.items()
            if not isinstance(primitive, CFP.Start)
        }:
            raise SolverError("Could not find guards for all primitives!")

        return guards
