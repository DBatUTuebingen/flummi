from enum import StrEnum


class SystemVariable(StrEnum):
    LABEL = "🏷️"
    RESULT = "📊"
    CONTROL = "⚙️"
    ITERATION = "#️⃣"
    PROBE = "🔍"


PROGRAM_VARIABLE = "$program#{idx}"


class Names(StrEnum):
    LOOP = "🔄"
    EXPRESSION = "ℚ"


def result_column(index: int) -> str:
    return f"{SystemVariable.RESULT}.{index + 1}"
