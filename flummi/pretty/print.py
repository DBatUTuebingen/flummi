from contextlib import contextmanager
from textwrap import indent, dedent

from ..grammars import CFG


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
    def EMITS(self): return self.keyword('EMITS')

    @property
    def INPUTS(self): return self.keyword('INPUTS')

    @property
    def IN(self): return self.keyword('IN')

    @property
    def VARS(self): return self.keyword('VARS')

    @property
    def BLOCKS(self): return self.keyword('BLOCKS')

    @property
    def JUMPS(self): return self.keyword('JUMPS')

    @property
    def BLOCK(self): return self.keyword('BLOCK')

    @property
    def EMIT(self): return self.keyword('EMIT')

    @property
    def JUMP(self): return self.keyword('JUMP')

    @property
    def GOTO(self): return self.keyword('GOTO')

    @property
    def STOP(self): return self.keyword('STOP')

    @property
    def IF(self): return self.keyword('IF')

    @property
    def THEN(self): return self.keyword('THEN')

    @property
    def ELSE(self): return self.keyword('ELSE')

    @property
    def FROM(self): return self.keyword('FROM')

    @property
    def TO(self): return self.keyword('TO')

    @property
    def WITH(self): return self.keyword('WITH')

    @property
    def WHERE(self): return self.keyword('WHERE')

    @property
    def NOT(self): return self.keyword('NOT')

    @property
    def AND(self): return self.keyword('AND')

    @property
    def TRUE(self): return self.keyword('TRUE')

    @property
    def LOOP(self): return self.keyword('LOOP')

    @property
    def AS(self): return self.keyword('AS')

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


STYLE = Color()


def pretty(node: CFG.Node[str, str]) -> str:
    match node:
        case CFG.Graph(entry_label, inputs, emits, variables, blocks, jumps):
            inputs = (
                '\n' * (0 < len(inputs)) +
                indent(f'{STYLE.COMMA}\n'.join(
                    f"{variable!s} {STYLE.LARROW} {expression!s}"
                    for variable, expression in inputs.items()
                ), ' '*18) +
                ('\n' + ' '*16) * (0 < len(inputs))
            )

            variables = (
                '\n' * (0 < len(variables)) +
                indent(f'{STYLE.COMMA}\n'.join(
                    f"{variable!s} {STYLE.COLON} {type!s}"
                    for variable, type in variables.items()
                ), ' '*18) +
                ('\n' + ' '*16) * (0 < len(variables))
            )

            blocks = (
                '\n' * (0 < len(blocks)) +
                indent('\n\n'.join(map(pretty, blocks.values())), ' '*18) +
                ('\n' + ' '*16) * (0 < len(blocks))
            )
            jumps = (
                '\n' * (0 < len(jumps)) +
                indent(',\n'.join(map(pretty, jumps)), ' '*18) +
                ('\n' + ' '*16) * (0 < len(jumps))
            )

            return dedent(f"""
                {STYLE.ENTRYPOINT} {STYLE.label(entry_label)}
                {STYLE.INPUTS} {STYLE.LPAREN}{inputs}{STYLE.RPAREN}
                {STYLE.EMITS} {emits!s}
                {STYLE.VARS} {STYLE.LPAREN}{variables}{STYLE.RPAREN}
                {STYLE.BLOCKS} {STYLE.LBRACE}{blocks}{STYLE.RBRACE}
                {STYLE.JUMPS} {STYLE.LBRACK}{jumps}{STYLE.RBRACK}
            """)[1:-1]

        case CFG.Block(block_label, parameters, statements, terminal, predecessor_references):
            parameters = STYLE.COMMA.join(map(str, parameters))
            predecessor_references = (
                '\n' * (0 < len(predecessor_references)) +
                indent(',\n'.join(map(pretty, predecessor_references)), ' '*18) +
                ('\n' + ' '*16) * (0 < len(predecessor_references))
            )
            statements = (
                '\n' * (0 < len(statements)) +
                indent(f'{STYLE.SEMI}\n'.join(map(pretty, statements)), ' '*18) +
                STYLE.SEMI * (0 < len(statements))
            )
            terminal = _indent(pretty(terminal), ' '*18)

            return dedent(f"""
                {STYLE.BLOCK} {STYLE.label(block_label)} {STYLE.LPAREN}{parameters}{STYLE.RPAREN}
                {STYLE.LBRACK}{predecessor_references}{STYLE.RBRACK}
                {STYLE.LBRACE}{statements}
                  {terminal}
                {STYLE.RBRACE}
            """)[1:-1]

        case CFG.Emit(to_emit):
            return f"{STYLE.EMIT} {to_emit!s}"

        case CFG.Assignment(variable, expression):
            indent_len = len(variable.identifier) + 5
            return f"{variable} {STYLE.LARROW} {_indent(str(expression), ' '*indent_len)}"

        case CFG.Jump(target, arguments):
            return f"{STYLE.JUMP} {STYLE.label(target)} {STYLE.LPAREN}{STYLE.COMMA.join(map(str, arguments))}{STYLE.RPAREN}"

        case CFG.GoTo(target, arguments):
            return f"{STYLE.GOTO} {STYLE.label(target)} {STYLE.LPAREN}{STYLE.COMMA.join(map(str, arguments))}{STYLE.RPAREN}"

        case CFG.Stop():
            return f"{STYLE.STOP}"

        case CFG.If(condition, truthy, falsey):
            return f"{STYLE.IF} {condition}\n{STYLE.THEN} {_indent(pretty(truthy), ' '*5)}\n{STYLE.ELSE} {_indent(pretty(falsey), ' '*5)}"

        case CFG.JumpDirective(origin, destination, parameters, predicate):
            return f"{STYLE.FROM} {STYLE.label(origin)} {STYLE.TO} {STYLE.label(destination)}\n{STYLE.WITH} {STYLE.LPAREN}{STYLE.COMMA.join(map(str, parameters))}{STYLE.RPAREN}\n{STYLE.WHERE} {pretty(predicate)}"

        case CFG.Variable(variable):
            return str(variable)

        case CFG.Not(operand):
            return f"{STYLE.NOT} {STYLE.LPAREN}{pretty(operand)}{STYLE.RPAREN}"

        case CFG.And(left, right):
            return f"{STYLE.LPAREN}{pretty(left)}{STYLE.RPAREN} {STYLE.AND} {STYLE.LPAREN}{pretty(right)}{STYLE.RPAREN}"

        case CFG.Tautology():
            return f"{STYLE.TRUE}"

        case CFG.FromLoop(expected_label):
            return f"{STYLE.FROM} {STYLE.LOOP} {STYLE.AS} {expected_label.label}"

        case CFG.FromBlock(target_label, arguments, predicate):
            return f"{STYLE.FROM} {STYLE.label(target_label)}\n{STYLE.WITH} {STYLE.LPAREN}{STYLE.COMMA.join(map(str, arguments))}{STYLE.RPAREN}\n{STYLE.WHERE} {pretty(predicate)}"

        case _:
            raise TypeError("Unknown CFG form.")
