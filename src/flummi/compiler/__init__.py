from ..library.sql import SQL
from ..library.errors import PrettyError
from ..IR.AST import Program


from .parsing import parse
from .analysis import analyze
from .lowering import lower
from .solving import solve
from .scheming import scheme
from .generation import generate

__all__ = ("compile",)


def compile(program: str | Program, source: str | None = None) -> SQL:
    try:
        if isinstance(program, str):
            source = program
            program = parse(program)

        analysis = analyze(program)

        lowered_program = lower(program)

        dataflow = solve(lowered_program, analysis)

        schema = scheme(lowered_program, analysis, dataflow)

        sql = generate(lowered_program, analysis, dataflow, schema)

        return sql
    except PrettyError as e:
        e.source = source
        raise e
