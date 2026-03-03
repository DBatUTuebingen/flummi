from enum import StrEnum


class SystemVariable(StrEnum):
    LABEL = "@label"
    RESULT = "@result"
    CONTROL = "@control"
    ITERATION = "@iteration"


PROGRAM_VARIABLE = "@prg#{idx}"


class Names(StrEnum):
    LOOP = "@loop"
