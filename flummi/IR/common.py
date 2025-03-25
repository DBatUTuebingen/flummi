from __future__ import annotations
from dataclasses import dataclass, field


__all__ = (
  "Annotated",
  "Expression",
  "Identifier",
  "Type",
  "Program",
  "Function",
)


@dataclass(kw_only=True, match_args=False)
class Annotated[A]:
  annotation: A = field(hash=False, compare=False, repr=False)


@dataclass
class Expression[A](Annotated[A]):
  source: str
  arguments: list[Identifier[A]]


@dataclass(unsafe_hash=True, order=True)
class Identifier[A](Annotated[A]):
  identifier: str


@dataclass
class Type[A](Annotated[A]):
  source: str


@dataclass
class Program[A, B](Annotated[A]):
  statement: B
  function_list: list[Function[A, B]]

  @property
  def functions(self) -> dict[Identifier[A], Function[A, B]]:
    return {
        function.name: function
        for function in self.function_list
    }


@dataclass
class Function[A, B](Annotated[A]):
  name: Identifier[A]
  parameters: dict[Identifier[A], Type[A]]
  return_type: Type[A]
  body: B
