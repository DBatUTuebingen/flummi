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


def prefix_token(prefix: SQL, content: SQL) -> SQL:
    return f"{prefix} {_indent(dedent(content), ' ' * (1 + len(prefix)))}\n"

_name = name


def variable(column: str, row: str | None = None) -> SQL:
    row = name(row) + "." if row else ""
    return row + name(column)


def paren(thing: SQL) -> SQL:
    return f"({_indent(dedent(thing), ' ')})"


def union_all(subqueries: list[SQL]) -> SQL:
    return "\n  UNION ALL\n".join(map(paren, map(dedent, subqueries)))


def select(
    select_list: list[SQL],
    from_list: list[SQL],
    joins: list[SQL] | None = None,
    predicates: list[SQL] | None = None,
    group_keys: list[SQL] | None = None,
    having: list[SQL] | None = None
) -> SQL:
    query = (
        f"SELECT {_indent(",\n".join(map(dedent, select_list)), ' ' * 7)}\n"
        f"FROM   {_indent(",\n".join(map(dedent, from_list)), ' ' * 7)}"
    )

    if joins:
        query += "\n".join(
            dedent(join)
            for join in joins
        )

    if predicates:
        query += "\nWHERE  " + "\nAND    ".join(
            _indent(dedent(predicate), ' ' * 7)
            for predicate in predicates
        )

    if group_keys:
        query += "\nGROUP  BY " + "\n, ".join(
            _indent(dedent(key), ' ' * 10)
            for key in group_keys
        )

        if having:
            query += "\nHAVING " + "\n, ".join(
                _indent(dedent(predicate), ' ' * 7)
                for predicate in having
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


def join(type: SQL, relation: SQL, predicates: list[SQL] | None = None) -> SQL:
    type += " JOIN"
    join = f"{type} {_indent(dedent(relation), ' ' * (1 + len(type)))}"

    if predicates:
        join += "\nON  " + "\nAND ".join(
            _indent(dedent(predicate), ' ' * 4)
            for predicate in predicates
        )

    return join


def call(function: str, arguments: list[SQL]) -> SQL:
    return f"{function}(" + "\n,".join(
        _indent(dedent(argument), ' ' * (1 + len(function)))
        for argument in arguments
    ) + ")"


def window(
    expression: SQL,
    partition_by: list[SQL] | None = None,
    order_by: list[SQL] | None = None,
    rows: SQL | tuple[SQL, SQL] | None = None,
    range: SQL | tuple[SQL, SQL] | None = None,
) -> SQL:
    window = ""

    if partition_by:
        window += "\nPARTITION BY " + "\n, ".join(
            _indent(dedent(key), ' ' * 13)
            for key in partition_by
        )

    if order_by:
        window += "\nORDER BY " + "\n, ".join(
            _indent(dedent(key), ' ' * 9)
            for key in order_by
        )

    if rows:
        if isinstance(rows, tuple):
            preceding, following = rows
            window += "\nROWS BETWEEN " + preceding + "\n"
            window +=   "     AND     " + following
        else:
            window += "\nROWS " + _indent(dedent(rows), ' ' * 5)
    elif range:
        if isinstance(range, tuple):
            preceding, following = range
            window += "\nRANGE BETWEEN " + preceding + "\n"
            window +=   "      AND     " + following
        else:
            window += "\nRANGE " + _indent(dedent(range), ' ' * 6)

    return expression + "OVER (" + _indent(window, '  ') + ")"