from dataclasses import dataclass
from typing import ClassVar

from .grammar import Location


__all__ = (
  "FlummiError",
)


@dataclass
class FlummiError(Exception):
  message: str
  location: Location

  name: ClassVar[str] = "Error"

  def __init_subclass__(cls, name: str) -> None:
    super().__init_subclass__()
    cls.name = name

  def format(self, source: str, *, lookahed: int = 2, lookbehind: int = 2) -> str:
    lines = source.splitlines()
    first_line = max(0, self.location.line - lookahed)
    local_line = self.location.line - first_line
    last_line = min(len(lines), self.location.line + lookbehind)

    annotated_source = [
      f"{1 + i + first_line: >{len(str(last_line))}} | {line}"
      for i, line in enumerate(lines[first_line:last_line])
    ]
    marker = "-" * (len(str(last_line)) + 3 + self.location.column) + "^"

    return "\n".join([
      *annotated_source[:local_line],
      marker,
      *annotated_source[local_line:],
      "",
      f"{self.name}: {self.message}"
    ])
