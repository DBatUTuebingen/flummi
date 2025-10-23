from enum import Flag, auto, unique


@unique
class Features(Flag):
    SEQUENCING = auto()
    BRANCHING = auto()
    ITERATION = auto()


FEATURE_DEPENDECIES = {
    Features.BRANCHING: Features.SEQUENCING,
    Features.ITERATION: Features.BRANCHING | Features.SEQUENCING,
}
