from enum import StrEnum


class Names(StrEnum):
    LABEL = "@label"
    RESULT = "@result"
    PROGRAM = "@program#{idx}"
    NOTHING = "@nothing"
    GUARD = "@guard"
    WORKING_TABLE = "@loop"
    INITIALIZATION = "@init"
