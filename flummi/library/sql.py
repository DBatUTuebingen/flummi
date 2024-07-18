from textwrap import indent, dedent
from .utils import *


__all__ = (
    "SQL",
    "NULL",
    "name",
    "named",
    "string",
    "variable",
    "union_all",
    "select",
    "cte",
    "with_ctes",
    "cast",
    "lateral",
    "paren"
)


type SQL = str


NULL: SQL = "NULL"


def string(content: str) -> SQL:
    return f"'{content}'"


def name(name: str) -> SQL:
    return f'"{name}"'


_name = name


def variable(column: str, row: str | None = None) -> SQL:
    row = name(row) + "." if row else ""
    return row + name(column)


def paren(thing: SQL) -> SQL:
    return f"({_indent(dedent(thing), ' ')})"


def union_all(subqueries: list[SQL]) -> SQL:
    return "\n  UNION ALL\n".join(map(paren, map(dedent, subqueries)))


def select(select_list: list[SQL], from_list: list[SQL], predicates: list[SQL] | None = None) -> SQL:
    query = (
        f"SELECT {_indent(",\n".join(map(dedent, select_list)), ' ' * 7)}\n"
        f"FROM   {_indent(",\n".join(map(dedent, from_list)), ' ' * 7)}"
    )

    if predicates:
        query += "\nWHERE  " + "\nAND    ".join(
            _indent(dedent(predicate), ' ' * 7)
            for predicate in predicates
        )

    return query


def cte(name: str, columns: list[str], body: SQL, materialize: bool = False) -> SQL:
    return (
        f"{_name(name)}({", ".join(map(_name, columns))}) AS{" MATERIALIZE" * materialize} (\n" +
        indent(dedent(body), "  ") +
        "\n)"
    )


def with_ctes(ctes: list[SQL], body: SQL, recursive: bool = False) -> SQL:
    return (
        f"WITH{" RECURSIVE" * recursive}\n" +
        indent(",\n".join(map(dedent, ctes)), "  ") +
        f"\n{dedent(body)}"
    )

def cast(expression: SQL, type: SQL) -> SQL:
    return f"CAST({_indent(paren(expression), " " * 6)} AS {type})"


def named(thing: SQL, name: str, columns: list[str] | None = None) -> SQL:
    named_thing = f"{thing} AS {_name(name)}"

    if columns:
        named_thing += f"({", ".join(map(_name, columns))})"

    return named_thing


def lateral(subquery: SQL) -> SQL:
    return f"LATERAL ({_indent(dedent(subquery), ' ' * 9)})"
