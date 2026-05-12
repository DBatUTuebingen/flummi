from functools import singledispatch

from ..library.sql import SQL
from ..IR.AST import Program

from .parsing import parse
from .analysis import analyze
from .lowering import lower
from .solving import solve
from .allocation import allocate
from .generation import generate

__all__ = ("compile",)


@singledispatch
def compile(source: str | Program) -> SQL: ...


@compile.register
def _(source: str) -> SQL:
    program = parse(source)

    return compile(program)


@compile.register
def _(program: Program) -> SQL:
    analysis = analyze(program)

    lowered_program = lower(program)

    dataflow = solve(lowered_program, analysis)

    allocation = allocate(lowered_program, analysis, dataflow)

    sql = generate(lowered_program, analysis, dataflow, allocation)

    return sql
