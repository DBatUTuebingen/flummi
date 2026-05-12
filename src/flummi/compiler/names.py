from enum import StrEnum


class SystemVariable(StrEnum):
    LABEL = ""
    RESULT = "󱕍"
    CONTROL = ""
    ITERATION = "󰐤"
    PROBE = ""


PROGRAM_VARIABLE = "$program#{idx}"


class Names(StrEnum):
    LOOP = "🔄"
    EXPRESSION = "ℚ"
