from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar

from rich.panel import Panel
from rich.text import Text
from rich.console import Group, RenderableType


__all__ = ("PrettyError", "Location")


@dataclass(unsafe_hash=True, order=True)
class Location:
    line: int
    column: int


type Reason = str | Location


class PrettyError(Exception):
    lookahead: ClassVar[int] = 2
    lookbehind: ClassVar[int] = 2

    reasoning: Iterable[Reason]

    def __init__(self, *reasoning: Reason):
        self.reasoning = reasoning
        super().__init__()

    def rich_format(self, source: str) -> Panel:
        formatted_reasons: list[RenderableType] = []
        for reason in self.reasoning:
            if isinstance(reason, Location):
                formatted_reasons.append(
                    Panel(
                        format_location(
                            source,
                            reason,
                            lookahead=self.lookahead,
                            lookbehind=self.lookbehind,
                        ),
                        border_style="dim",
                    )
                )
            else:
                formatted_reasons.append(Text.from_markup(reason))

        return Panel.fit(
            Group(*formatted_reasons),
            title=f"[bold red]{type(self).__name__}[/bold red]",
            title_align="left",
            border_style="red",
        )


def format_location(
    source: str, location: Location, *, lookahead: int = 2, lookbehind: int = 2
) -> str:
    lines = source.splitlines()
    first_line = max(0, location.line - lookahead)
    local_line = location.line - first_line
    last_line = min(len(lines), location.line + lookbehind)

    annotated_source = [
        f"[cyan]{1 + i + first_line: >{len(str(last_line))}}[/cyan] [bold]│[/bold] {line.replace('[', r'\[')}"
        for i, line in enumerate(lines[first_line:last_line])
    ]
    marker = (
        "[bold red]"
        + "─" * (len(str(last_line)) + 3 + location.column - 1)
        + "╯[/bold red]"
    )

    return "\n".join(
        [
            *annotated_source[:local_line],
            marker,
            *annotated_source[local_line:],
        ]
    )
