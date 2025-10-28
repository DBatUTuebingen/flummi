from textwrap import indent, dedent
from .utils import indent1


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
    "paren",
    "case",
    "when",
)


type SQL = str


NULL: SQL = "NULL"


def string(content: str) -> SQL:
    return f"'{content}'"


def name(name: str) -> SQL:
    return f'"{name}"'


def prefix_token(prefix: SQL, content: SQL) -> SQL:
    return f"{prefix} {indent1(dedent(content), ' ' * (1 + len(prefix)))}\n"


_name = name


def variable(column: str, row: str | None = None) -> SQL:
    row = name(row) + "." if row else ""
    return row + name(column)


def paren(thing: SQL) -> SQL:
    return f"({indent1(dedent(thing), ' ')})"


def union_all(subqueries: list[SQL]) -> SQL:
    return "\n  UNION ALL\n".join(map(paren, map(dedent, subqueries)))


def select(
    select_list: list[SQL],
    from_list: list[SQL] | None = None,
    joins: list[SQL] | None = None,
    predicates: list[SQL] | None = None,
    group_keys: list[SQL] | None = None,
    having: list[SQL] | None = None,
    distinct: bool = False,
) -> SQL:
    query = "SELECT "

    if distinct:
        query += "DISTINCT \n" + " " * 7

    query += indent1(",\n".join(map(dedent, select_list)), " " * 7)

    if from_list:
        query += (
            f"\nFROM   {indent1(',\n'.join(map(dedent, from_list)), ' ' * 7)}"
        )

        if joins:
            query += "\n".join(dedent(join) for join in joins)

    if predicates:
        query += "\nWHERE  " + "\nAND    ".join(
            indent1(dedent(predicate), " " * 7) for predicate in predicates
        )

    if from_list:
        if group_keys:
            query += "\nGROUP  BY " + ",\n          ".join(
                indent1(dedent(key), " " * 10) for key in group_keys
            )

            if having:
                query += "\nHAVING " + "\nAND    ".join(
                    indent1(dedent(predicate), " " * 7) for predicate in having
                )

    return query


def cte(
    name: str, columns: list[str], body: SQL, materialize: bool = False
) -> SQL:
    return (
        f"{_name(name)}({', '.join(map(_name, columns))}) AS{' MATERIALIZED' * materialize} (\n"
        + indent(dedent(body), "  ")
        + "\n)"
    )


def typed_cte(name: str, columns: dict[str, SQL], body: SQL) -> SQL:
    return (
        f"{_name(name)}({', '.join(f'{_name(column)} {type}' for column, type in columns.items())}) "
        + "AS (\n"
        + indent(dedent(body), "  ")
        + "\n)"
    )


def with_ctes(
    ctes: list[SQL],
    body: SQL,
    recursive: bool = False,
    mutually_recursive: bool = False,
) -> SQL:
    assert not (recursive and mutually_recursive)
    return (
        f"WITH{' MUTUALLY' * mutually_recursive}{' RECURSIVE' * (recursive + mutually_recursive)}\n"
        + indent(",\n".join(map(dedent, ctes)), "  ")
        + f"\n{dedent(body)}"
    )


def cast(expression: SQL, type: SQL) -> SQL:
    return f"CAST({indent1(paren(expression), ' ' * 6)} AS {type})"


def named(thing: SQL, name: str, columns: list[str] | None = None) -> SQL:
    named_thing = f"{thing} AS {_name(name)}"

    if columns:
        named_thing += f"({', '.join(map(_name, columns))})"

    return named_thing


def lateral(subquery: SQL) -> SQL:
    return f"LATERAL ({indent1(dedent(subquery), ' ' * 9)})"


def join(type: SQL, relation: SQL, predicates: list[SQL] | None = None) -> SQL:
    type += " JOIN"
    join = f"{type} {indent1(dedent(relation), ' ' * (1 + len(type)))}"

    if predicates:
        join += "\nON  " + "\nAND ".join(
            indent1(dedent(predicate), " " * 4) for predicate in predicates
        )

    return join


def call(function: str, arguments: list[SQL] | None = None) -> SQL:
    return (
        f"{function}("
        + indent1(
            ",\n".join(dedent(argument) for argument in arguments or []),
            " " * (1 + len(function)),
        )
        + ")"
    )


def window(
    expression: SQL,
    partition_by: list[SQL] | None = None,
    order_by: list[SQL] | None = None,
    rows: SQL | tuple[SQL, SQL] | None = None,
    range: SQL | tuple[SQL, SQL] | None = None,
) -> SQL:
    window = ""

    if partition_by:
        window += "\nPARTITION BY " + ",\n             ".join(
            indent1(dedent(key), " " * 13) for key in partition_by
        )

    if order_by:
        window += "\nORDER BY " + ",\n         ".join(
            indent1(dedent(key), " " * 9) for key in order_by
        )

    if rows:
        if isinstance(rows, tuple):
            preceding, following = rows
            window += "\nROWS BETWEEN " + preceding + "\n"
            window += "     AND     " + following
        else:
            window += "\nROWS " + indent1(dedent(rows), " " * 5)
    elif range:
        if isinstance(range, tuple):
            preceding, following = range
            window += "\nRANGE BETWEEN " + preceding + "\n"
            window += "      AND     " + following
        else:
            window += "\nRANGE " + indent1(dedent(range), " " * 6)

    return expression + " OVER (" + indent1(window, "  ") + ")"


def case(*whens: SQL, default: SQL | None = None) -> SQL:
    case_expression = "CASE\n"
    for when in whens:
        case_expression += indent(when, "  ")
    if default:
        case_expression += "  ELSE " + indent1(default, " " * 7) + "\n"
    case_expression += "END"
    return case_expression


def when(condition: SQL, body: SQL) -> SQL:
    output = ""
    output += "WHEN " + indent1(condition, " " * 5) + "\n"
    output += "THEN " + indent1(body, " " * 5) + "\n"
    return output


def values(*rows: tuple[SQL, ...]) -> SQL:
    return "VALUES " + indent1(
        "\n".join(paren(",".join(row)) for row in rows), " " * 9
    )
