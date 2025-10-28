from enum import Enum, auto, unique


@unique
class Feature(Enum):
    SEQUENCING = auto()
    BRANCHING = auto()
    ITERATION = auto()
    CONCURRENCY = auto()


type Features = set[Feature]

MINIMAL_FEATURES = {Feature.SEQUENCING}

FEATURE_DEPENDECIES = {
    Feature.BRANCHING: {Feature.SEQUENCING},
    Feature.ITERATION: {
        Feature.BRANCHING,
        Feature.SEQUENCING,
    },
}
