from enum import Flag, auto, unique


@unique
class Features(Flag):
    SEQUENCING = auto()
    BRANCHING = auto()


FEATURE_DEPENDECIES = {
    Features.BRANCHING: Features.SEQUENCING,
}
