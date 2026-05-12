from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar

__all__ = ("Location", "PrettyError")


@dataclass(unsafe_hash=True, order=True)
class Location:
    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.line}:{self.column}"


class PrettyError(Exception):
    base_exception: ClassVar[type[Exception]]
    lookahead: ClassVar[int] = 2
    lookbehind: ClassVar[int] = 2

    reasoning: Iterable[str | Location]
    source: str | None = None

    def __init__(self, *reasoning: str | Location):
        self.reasoning = reasoning
        super().__init__()

    def format(self) -> str:
        formatted_reasons = [f"{type(self).__name__}:"]
        for reason in self.reasoning:
            if isinstance(reason, Location):
                formatted_reasons.append(
                    format_location(
                        self.source,
                        reason,
                        lookahead=self.lookahead,
                        lookbehind=self.lookbehind,
                    )
                    if self.source
                    else f"<no source available>@{reason}"
                )
            else:
                formatted_reasons.append(reason)

        return "\n".join(formatted_reasons)

    def __str__(self) -> str:
        return self.format()


def format_location(
    source: str, location: Location, *, lookahead: int = 2, lookbehind: int = 2
) -> str:
    lines = source.splitlines()
    first_line = max(0, location.line - lookahead)
    local_line = location.line - first_line
    last_line = min(len(lines), location.line + lookbehind)

    annotated_source = [
        f"{1 + i + first_line: >{len(str(last_line))}} | {line}"
        for i, line in enumerate(lines[first_line:last_line])
    ]
    marker = "-" * (len(str(last_line)) + 3 + location.column - 1) + "^"

    return "\n".join(
        [*annotated_source[:local_line], marker, *annotated_source[local_line:]]
    )
