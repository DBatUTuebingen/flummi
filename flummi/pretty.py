from dataclasses import dataclass
from itertools import chain
from textwrap import indent, dedent

from . import CFG, grammar
from .utils import _indent


@dataclass
class Style:
    keyword_style: str = "1;34"
    punctuation_style: str = "2"
    label_style: str = "4"
    external_style: str = "2;3"

    active: bool = True

    def off(self):
        self.active = False

    def on(self):
        self.active = True

    def _style(self, style: str, to_style: str) -> str:
        if self.active:
            return f"\033[{style}m{to_style}\033[0m"
        else:
            return to_style

    def keyword(self, word: str) -> str:
        return self._style(self.keyword_style, word)

    def punctuation(self, op: str) -> str:
        return self._style(self.punctuation_style, op)

    def label(self, label: CFG.BlockLabel) -> str:
        return self._style(self.label_style, label.label)

    def external(self, content: str) -> str:
        return self._style(self.external_style, content)

    @property
    def ENTRYPOINT(self): return self.keyword('ENTRYPOINT')

    @property
    def IN(self): return self.keyword('IN')

    @property
    def BLOCKS(self): return self.keyword('BLOCKS')

    @property
    def BLOCK(self): return self.keyword('BLOCK')

    @property
    def EMIT(self): return self.keyword('EMIT')

    @property
    def JUMP(self): return self.keyword('JUMP')

    @property
    def GOTO(self): return self.keyword('GOTO')

    @property
    def WHERE(self): return self.keyword('WHERE')

    @property
    def NOT(self): return self.keyword('NOT')

    @property
    def AND(self): return self.keyword('AND')

    @property
    def LOOP(self): return self.keyword('LOOP')

    @property
    def BREAK(self): return self.keyword('BREAK')

    @property
    def CONTINUE(self): return self.keyword('CONTINUE')

    @property
    def STOP(self): return self.keyword('STOP')

    @property
    def NOOP(self): return self.keyword('NOOP')

    @property
    def FUN(self): return self.keyword('FUN')

    @property
    def CALL(self): return self.keyword('CALL')

    @property
    def IF(self): return self.keyword('IF')

    @property
    def THEN(self): return self.keyword('THEN')

    @property
    def ELSE(self): return self.keyword('ELSE')

    @property
    def SPAWN(self): return self.keyword('SPAWN')

    @property
    def AS(self): return self.keyword('AS')

    @property
    def JOIN(self): return self.keyword('JOIN')

    @property
    def FETCH(self): return self.keyword('FETCH')

    @property
    def INTO(self): return self.keyword('INTO')

    @property
    def DONE(self): return self.keyword('DONE')

    @property
    def VAR(self): return self.keyword('VAR')

    @property
    def COMMA(self): return self.punctuation(',')

    @property
    def SEMI(self): return self.punctuation(';')

    @property
    def COLON(self): return self.punctuation(':')

    @property
    def LPAREN(self): return self.punctuation('(')

    @property
    def RPAREN(self): return self.punctuation(')')

    @property
    def LBRACK(self): return self.punctuation('[')

    @property
    def RBRACK(self): return self.punctuation(']')

    @property
    def LBRACE(self): return self.punctuation('{')

    @property
    def RBRACE(self): return self.punctuation('}')

    @property
    def LARROW(self): return self.punctuation('<-')

    @property
    def RARROW(self): return self.punctuation('->')

    @property
    def PARA(self): return self.punctuation('§')


STYLE = Style()


def pretty(node: CFG.Node | grammar.Node, *, style: Style = STYLE) -> str:
    match node:
        case CFG.Graph(entry_label, _, blocks):
            blocks = (
                '\n' * (0 < len(blocks)) +
                indent('\n\n'.join(map(pretty, blocks.values())), ' '*18) +
                ('\n' + ' '*16) * (0 < len(blocks))
            )

            return dedent(f"""
                {style.ENTRYPOINT} {style.label(entry_label)}
                {style.BLOCKS} {style.LBRACE}{blocks}{style.RBRACE}
            """)[1:-1]

        case CFG.Block(block_label, statements, terminals):
            statements = _indent(f'\n'.join(map(pretty, statements)), ' '*18)
            terminals = _indent('\n'.join(map(pretty, terminals)), ' '*18)

            return dedent(f"""
                {style.BLOCK} {style.label(block_label)} {style.LBRACE}
                  {statements}{('\n' + ' ' * 18) * bool(statements)}{terminals}
                {style.RBRACE}
            """)[1:-1]

        case CFG.Assignment(variables, expression) | grammar.Assignment(_, variables, expression):
            variables = f"{style.COMMA} ".join(map(pretty, variables))
            return f"{variables} {style.LARROW} {_indent(pretty(expression), ' ' * (len(variables) + 4))}"

        case CFG.Terminal(type, truthy_vars, falsey_vars):
            predicate = f" {style.AND} ".join(chain(
                (                  pretty(var) for var in truthy_vars),
                (f"{style.NOT} " + pretty(var) for var in falsey_vars),
            ))
            if predicate:
                predicate = f" {style.WHERE} {predicate}"
            return pretty(type) + predicate

        case CFG.Emit(to_emit) | grammar.Emit(_, to_emit):
            variables = f"{style.COMMA} ".join(map(pretty, to_emit))
            return f"{style.EMIT} {variables}"

        case CFG.Jump(target):
            return f"{style.JUMP} {style.label(target)}"

        case CFG.GoTo(target):
            return f"{style.GOTO} {style.label(target)}"

        case grammar.Type(_, source):
            return style.external(f"§{_indent(source, ' ')}§")

        case grammar.Expression(_, source, free_variables):
            return (
                f"{style.PARA}{style.external(_indent(source, ' '))}{style.PARA}"
                f"{style.LBRACK}{f"{style.COMMA} ".join(map(pretty, free_variables))}{style.RBRACK}"
            )

        case grammar.Declaration(_, variables, type):
            variables = f"{style.COMMA} ".join(map(pretty, variables))
            return f"{variables} {style.COLON} {_indent(pretty(type), ' ' * (len(variables) + 3))}"

        case grammar.Variable(_, identifier):
            return identifier

        case grammar.NoOp(_):
            return style.NOOP

        case grammar.Stop(_):
            return style.STOP

        case grammar.Continue(_, loop_label):
            return f"{style.CONTINUE} {pretty(loop_label)}"

        case grammar.Break(_, loop_label):
            return f"{style.BREAK} {pretty(loop_label)}"

        case grammar.Block(_, statements):
            if statements:
                statements = f"{style.SEMI}\n  ".join(
                    _indent(pretty(statement), '  ')
                    for statement in statements
                )
                return f"{style.LBRACE}\n  {statements}\n{style.RBRACE}"
            else:
                return f"{style.LBRACE}{style.RBRACE}"

        case grammar.If(_, condition, truthy, falsey):
            return (
                f"{style.IF} {pretty(condition)}\n"
                f"{style.THEN} {pretty(truthy)}\n"
                f"{style.ELSE} {pretty(falsey)}"
            )

        case grammar.HandleCheck(_, handle):
            handle = pretty(handle)
            return f"{style.DONE} {handle}"

        case grammar.VariableCheck(_, variable):
            variable = pretty(variable)
            return f"{style.VAR} {variable}"

        case grammar.Loop(_, loop_label, body):
            return f"{style.LOOP} {pretty(loop_label)} {pretty(body)}"

        case grammar.Spawn(_, handle, target, arguments):
            handle = pretty(handle)
            target = pretty(target)
            arguments = f"{style.COMMA} ".join(map(pretty, arguments))
            return f"{style.SPAWN} {handle} {style.AS} {target}{style.LPAREN}{arguments}{style.RPAREN}"

        case grammar.Join(_, handle):
            handle = pretty(handle)
            return f"{style.JOIN} {handle}"

        case grammar.Fetch(_, handle, variables):
            handle = pretty(handle)
            variables = f"{style.COMMA} ".join(map(pretty, variables))
            return f"{style.FETCH} {handle} {style.INTO} {variables}"

        case grammar.Function(_, name, parameters, emits, body):
            name = pretty(name)
            parameters = f"{style.COMMA} ".join(
                f"{pretty(parameter)}{style.COLON} {pretty(type)}"
                for parameter, type in parameters.items()
            )
            emits = f"{style.COMMA} ".join(map(pretty, emits))
            body = pretty(body)
            return f"{style.FUN} {name}{style.LPAREN}{parameters}{style.RPAREN} {style.RARROW} {emits} {body}"

        case grammar.Program(_, main_function_name, inputs, function_list):
            main_function_name = pretty(main_function_name)
            inputs = pretty(inputs) if inputs is not None else ""
            function_list = "\n\n".join(map(pretty, function_list))
            return f"{style.CALL} {main_function_name}{style.LPAREN}{inputs}{style.RPAREN} {style.IN}\n{function_list}"

        case _:
            raise TypeError(f"Can't format {node!r}.")
