from ..library.sql import SQL

from .parsing import parse
from .analysis import analyze
from .lowering import lower
from .solving import solve
from .allocation import allocate
from .generation import generate

__all__ = ("compile",)


def compile(source: str) -> SQL:
    program = parse(source)

    analysis = analyze(program)

    lowered_program = lower(program)

    dataflow = solve(lowered_program, analysis)

    allocation = allocate(lowered_program, analysis, dataflow)

    sql = generate(lowered_program, analysis, dataflow, allocation)

    return sql
