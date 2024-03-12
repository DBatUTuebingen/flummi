from itertools import chain
from textwrap import indent, dedent

from .. import CFG, grammar


def _indent(lines: str, prefix: str):
    out = ""
    for i, line in enumerate(lines.splitlines(keepends=True)):
        if i > 0:
            out += prefix + line
        else:
            out += line
    return out


class Color:
    def __init__(self):
        self.active = True

    def off(self):
        self.active = False

    def on(self):
        self.active = True

    def __bool__(self):
        return self.active

    def keyword(self, word: str) -> str:
        if self.active:
            return f"\033[1;34m{word}\033[0m"
        else:
            return word

    @property
    def ENTRYPOINT(self): return self.keyword('ENTRYPOINT')

    @property
    def BLOCKS(self): return self.keyword('BLOCKS')

    @property
    def BLOCK(self): return self.keyword('BLOCK')

    @property
    def EMIT(self): return self.keyword('EMIT')

    @property
    def GOTO(self): return self.keyword('GOTO')

    @property
    def MANY(self): return self.keyword('MANY')

    @property
    def ONE(self): return self.keyword('ONE')

    @property
    def WHERE(self): return self.keyword('WHERE')

    @property
    def NOT(self): return self.keyword('NOT')

    @property
    def AND(self): return self.keyword('AND')

    def operator(self, op: str) -> str:
        if self.active:
            return f"\033[1;2m{op}\033[0m"
        else:
            return op

    @property
    def COMMA(self): return self.operator(',')

    @property
    def SEMI(self): return self.operator(';')

    @property
    def COLON(self): return self.operator(':')

    @property
    def LPAREN(self): return self.operator('(')

    @property
    def RPAREN(self): return self.operator(')')

    @property
    def LBRACK(self): return self.operator('[')

    @property
    def RBRACK(self): return self.operator(']')

    @property
    def LBRACE(self): return self.operator('{')

    @property
    def RBRACE(self): return self.operator('}')

    @property
    def LARROW(self): return self.operator('<-')

    @property
    def RARROW(self): return self.operator('->')

    @property
    def PARA(self): return self.operator('§')

    def label(self, label: CFG.BlockLabel) -> str:
        if self.active:
            return f"\033[4m{label.label}\033[0m"
        else:
            return label.label

    def external(self, content: str) -> str:
        if self.active:
            return f"\033[2m{content}\033[0m"
        else:
            return content


STYLE = Color()


def pretty(node: CFG.Graph | CFG.Block | CFG.Action | CFG.Terminal | CFG.TerminalType | grammar.Assignment | grammar.Valuedness | grammar.Argument | grammar.Expression) -> str:
    match node:
        case CFG.Graph(entry_label, blocks):
            blocks = (
                '\n' * (0 < len(blocks)) +
                indent('\n\n'.join(map(pretty, blocks.values())), ' '*18) +
                ('\n' + ' '*16) * (0 < len(blocks))
            )

            return dedent(f"""
                {STYLE.ENTRYPOINT} {STYLE.label(entry_label)}
                {STYLE.BLOCKS} {STYLE.LBRACE}{blocks}{STYLE.RBRACE}
            """)[1:-1]

        case CFG.Block(block_label, action, terminals):
            action = pretty(action) if action is not None else ""
            terminals = _indent('\n'.join(map(pretty, terminals)), ' '*18)

            return dedent(f"""
                {STYLE.BLOCK} {STYLE.label(block_label)} {STYLE.LBRACE}
                  {action}{('\n' + ' ' * 18) * bool(action)}{terminals}
                {STYLE.RBRACE}
            """)[1:-1]

        case CFG.ReducingAssignment(assignment):
            return pretty(assignment)

        case CFG.SpanningAssignments(assignments):
            return "\n".join(map(pretty, assignments))

        case grammar.Assignment(_, variables, expression):
            variables = ", ".join(variable.identifier for variable in variables)
            indent_len = len(variables) + 5
            return f"{variables} {STYLE.LARROW} {_indent(pretty(expression), ' '*indent_len)}"

        case grammar.Expression(_, valuedness, source, arguments):
            return f"{pretty(valuedness)} §{STYLE.external(source)}§[{', '.join(map(pretty, arguments))}]"

        case grammar.Argument(_, valuedness, variable):
            return f"{pretty(valuedness)} {variable.identifier}"

        case grammar.Valuedness.SET:
            return STYLE.MANY

        case grammar.Valuedness.SCALAR:
            return STYLE.ONE

        case CFG.Terminal(type, truthy_vars, falsey_vars):
            predicate = f" {STYLE.AND} ".join(chain(
                (                  var.identifier for var in truthy_vars),
                (f"{STYLE.NOT} " + var.identifier for var in falsey_vars),
            ))
            if predicate:
                predicate = f" {STYLE.WHERE} {predicate}"
            return pretty(type) + predicate

        case CFG.Emit(emit):
            return f"{STYLE.EMIT} {', '.join(map(str, emit.to_emit))}"

        case CFG.GoTo(target):
            return f"{STYLE.GOTO} {STYLE.label(target)}"

        case _:
            raise TypeError("Unknown CFG form.")
