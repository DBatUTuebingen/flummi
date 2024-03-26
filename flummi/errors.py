from typing import ClassVar

from .IR.AST import Location


__all__ = (
  "FlummiError",
)


class FlummiError(Exception):
    name: ClassVar[str] = "Error"

    def __init__(self, *reasoning: str | Location):
        self.reasoning = reasoning

    def __init_subclass__(cls, name: str) -> None:
        super().__init_subclass__()
        cls.name = name

    def format(self, source: str, *, lookahead: int = 2, lookbehind: int = 2) -> str:
        formatted_reasons = [
            f"[Encountered error during {self.name}]"
        ]
        for reason in self.reasoning:
            if isinstance(reason, Location):
                formatted_reasons.append(
                    format_location(
                        source,
                        reason,
                        lookahead=lookahead,
                        lookbehind=lookbehind,
                    )
                )
            else:
                formatted_reasons.append(reason)

        return "\n".join(formatted_reasons)


def format_location(
    source: str,
    location: Location,
    *,
    lookahead: int = 2,
    lookbehind: int = 2
) -> str:
    lines = source.splitlines()
    first_line = max(0, location.line - lookahead)
    local_line = location.line - first_line
    last_line = min(len(lines), location.line + lookbehind)

    annotated_source = [
      f"{1 + i + first_line: >{len(str(last_line))}} | {line}"
      for i, line in enumerate(lines[first_line:last_line])
    ]
    marker = "-" * (len(str(last_line)) + 3 + location.column) + "^"

    return "\n".join([
      *annotated_source[:local_line],
      marker,
      *annotated_source[local_line:]
    ])
