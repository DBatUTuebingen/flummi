from textwrap import indent, dedent
from typing import TypeVar


from ..grammars import CFG


def keyword(word: str) -> str:
    return f"\033[1;34m{word}\033[0m"

ENTRYPOINT = keyword('ENTRYPOINT')
EMITS = keyword('EMITS')
INPUTS = keyword('INPUTS')
IN = keyword('IN')
VARS = keyword('VARS')
BLOCKS = keyword('BLOCKS')
JUMPS = keyword('JUMPS')
BLOCK = keyword('BLOCK')
EMIT = keyword('EMIT')
JUMP = keyword('JUMP')
GOTO = keyword('GOTO')
STOP = keyword('STOP')
IF = keyword('IF')
THEN = keyword('THEN')
ELSE = keyword('ELSE')
FROM = keyword('FROM')
TO = keyword('TO')
WITH = keyword('WITH')
WHERE = keyword('WHERE')
NOT = keyword('NOT')
AND = keyword('AND')
TRUE = keyword('TRUE')
LOOP = keyword('LOOP')
AS = keyword('AS')


def operator(op: str) -> str:
    return f"\033[1;2m{op}\033[0m"


COMMA = operator(', ')
SEMI = operator(';')
COLON = operator(':')
LPAREN = operator('(')
RPAREN = operator(')')
LBRACK = operator('[')
RBRACK = operator(']')
LBRACE = operator('{')
RBRACE = operator('}')
LARROW = operator('<-')
RARROW = operator('->')
PARA = operator('§')


def label(label: CFG.BlockLabel) -> str:
    return f"\033[4m{label.label}\033[0m"


def pretty(node: CFG.Node[str, str]) -> str:
    match node:
        case CFG.Graph(entry_label, inputs, emits, variables, blocks, jumps):
            inputs = (
                '\n' * (0 < len(inputs)) +
                indent(f'{COMMA}\n'.join(
                    f"{variable!s} {LARROW} {expression!s}"
                    for variable, expression in inputs.items()
                ), ' '*18) +
                ('\n' + ' '*16) * (0 < len(inputs))
            )

            variables = (
                '\n' * (0 < len(variables)) +
                indent(f'{COMMA}\n'.join(
                    f"{variable!s} {COLON} {type!s}"
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
                indent('\n'.join(map(pretty, jumps)), ' '*18) +
                ('\n' + ' '*16) * (0 < len(jumps))
            )

            return dedent(f"""
                {ENTRYPOINT} {label(entry_label)}
                {INPUTS} {LPAREN}{inputs}{RPAREN}
                {EMITS} {emits!s}
                {VARS} {LPAREN}{variables}{RPAREN}
                {BLOCKS} {LBRACE}{blocks}{RBRACE}
                {JUMPS} {LBRACK}{jumps}{RBRACK}
            """)[1:-1]

        case CFG.Block(block_label, parameters, statements, terminal, predecessor_references):
            parameters = COMMA.join(map(str, parameters))
            predecessor_references = (
                '\n' * (0 < len(predecessor_references)) +
                indent('\n'.join(map(pretty, predecessor_references)), ' '*18) +
                ('\n' + ' '*16) * (0 < len(predecessor_references))
            )
            statements = (
                '\n' * (0 < len(statements)) +
                indent(f'{SEMI}\n'.join(map(pretty, statements)), ' '*18) +
                SEMI * (0 < len(statements))
            )
            terminal = pretty(terminal)

            return dedent(f"""
                {BLOCK} {label(block_label)} {LPAREN}{parameters}{RPAREN}
                {LBRACK}{predecessor_references}{RBRACK}
                {LBRACE}{statements}
                  {terminal}
                {RBRACE}
            """)[1:-1]

        case CFG.Emit(to_emit):
            return f"{EMIT} {to_emit!s}"

        case CFG.Assignment(variable, expression):
            return f"{variable} {LARROW} {expression!s}"

        case CFG.Jump(target, arguments):
            return f"{JUMP} {label(target)} {LPAREN}{COMMA.join(map(str, arguments))}{RPAREN}"

        case CFG.GoTo(target, arguments):
            return f"{GOTO} {label(target)} {LPAREN}{COMMA.join(map(str, arguments))}{RPAREN}"

        case CFG.Stop():
            return f"{STOP}"

        case CFG.If(condition, truthy, falsey):
            return f"{IF} {condition} {THEN} {pretty(truthy)} {ELSE} {pretty(falsey)}"

        case CFG.JumpDirective(origin, destination, parameters, predicate):
            return f"{FROM} {label(origin)} {TO} {label(destination)} {WITH} {LPAREN}{COMMA.join(map(str, parameters))}{RPAREN} {WHERE} {pretty(predicate)}"

        case CFG.Variable(variable):
            return str(variable)

        case CFG.Not(operand):
            return f"{NOT} {LPAREN}{pretty(operand)}{RPAREN}"

        case CFG.And(left, right):
            return f"{LPAREN}{pretty(left)}{RPAREN} {AND} {LPAREN}{pretty(right)}{RPAREN}"

        case CFG.Tautology():
            return f"{TRUE}"

        case CFG.FromLoop(expected_label):
            return f"{FROM} {LOOP} {AS} {expected_label.label}"

        case CFG.FromBlock(target_label, arguments, predicate):
            return f"{FROM} {label(target_label)} {WITH} {LPAREN}{COMMA.join(map(str, arguments))}{RPAREN} {WHERE} {pretty(predicate)}"

        case _:
            raise TypeError("Unknown CFG form.")
