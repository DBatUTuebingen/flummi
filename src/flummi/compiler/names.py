from enum import StrEnum


class SystemVariable(StrEnum):
    LABEL = "$label"
    RESULT = "$result"
    CONTROL = "$control"
    ITERATION = "$iteration"
    PROBE = "$probe"


PROGRAM_VARIABLE = "$program#{idx}"


class Names(StrEnum):
    LOOP = "@loop"
    EXPRESSION = "@expression"
