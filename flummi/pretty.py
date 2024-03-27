from dataclasses import dataclass
from itertools import chain
from textwrap import indent, dedent

from .IR import CFG, AST, common
from .utils import _indent


@dataclass
class Style:
    keyword_style: str = ""
    punctuation_style: str = ""
    label_style: str = ""
    external_style: str = ""

    def _style(self, style: str, to_style: str) -> str:
        if style:
            return f"\033[{style}m{to_style}\033[0m"
        else:
            return to_style

    def keyword(self, word: str) -> str:
        return self._style(self.keyword_style, word)

    def punctuation(self, op: str) -> str:
        return self._style(self.punctuation_style, op)

    def label(self, label: str) -> str:
        return self._style(self.label_style, label)

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
    def RETURN(self): return self.keyword('RETURN')

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
    def NOOP(self): return self.keyword('NOOP')

    @property
    def FUN(self): return self.keyword('FUN')

    @property
    def CALL(self): return self.keyword('CALL')

    @property
    def AS(self): return self.keyword('AS')

    @property
    def IF(self): return self.keyword('IF')

    @property
    def THEN(self): return self.keyword('THEN')

    @property
    def ELSE(self): return self.keyword('ELSE')

    @property
    def WAIT(self): return self.keyword('WAIT')

    @property
    def ON(self): return self.keyword('ON')

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
    def DLARROW(self): return self.punctuation('<=')

    @property
    def RARROW(self): return self.punctuation('->')

    @property
    def PARA(self): return self.punctuation('§')


CLI_STYLE = Style(
    keyword_style="1;34",
    punctuation_style="2",
    label_style="4",
    external_style="2;3",
)

BLANK_STYLE = Style()


type Printable = (
    common.Program |
    common.Function |
    common.Expression |
    common.Type |
    common.Identifier |
    AST.Statement |
    CFG.Node
)

def pretty(node, *, style: Style = BLANK_STYLE) -> str:
    match node:
        case common.Program(main_function_name, inputs, function_list):
            main_function_name = style.label(main_function_name.identifier)
            inputs = pretty(inputs, style=style) if inputs is not None else ""
            functions = "\n\n".join(map(pretty, function_list))

            return (
                f"{style.CALL} "
                f"{main_function_name}{style.LPAREN}{inputs}{style.RPAREN}\n"
                f"{functions}"
            )

        case common.Function(name, parameters, return_types, body):
            name = style.label(name.identifier)
            parameters = f"{style.COMMA} ".join(
                f"{pretty(parameter)}{style.COLON} {pretty(type, style=style)}"
                for parameter, type in parameters.items()
            )
            returns = f"{style.COMMA} ".join(
                pretty(type, style=style)
                for type in return_types
            )
            body = pretty(body)

            return (
                f"{style.FUN} {name}{style.LPAREN}{parameters}{style.RPAREN} "
                f"{style.RARROW} {returns} {body}"
            )

        case common.Type(source):
            return style.external(f"§{_indent(source, ' ')}§")

        case common.Expression(source, arguments):
            source = style.external(_indent(source, ' '))
            arguments = f"{style.COMMA} ".join(
                pretty(argument, style=style)
                for argument in arguments
            )
            return (
                f"{style.PARA}{source}{style.PARA}"
                f"{style.LBRACK}{arguments}{style.RBRACK}"
            )

        case common.Identifier(identifier):
            return identifier


        case AST.Return(variables):
            variables = f"{style.COMMA} ".join(
                pretty(variable, style=style)
                for variable in variables
            )
            return f"{style.RETURN} {variables}"

        case AST.Call(variables, function, arguments):
            variables = f"{style.COMMA} ".join(
                pretty(variable, style=style)
                for variable in variables
            )
            function = style.label(function.identifier)
            arguments = f"{style.COMMA} ".join(
                pretty(argument, style=style)
                for argument in arguments
            )
            return f"{variables} {style.DLARROW} {function}{style.LPAREN}{arguments}{style.RPAREN}"

        case AST.Declaration(variables, type):
            variables = f"{style.COMMA} ".join(
                pretty(variable, style=style)
                for variable in variables
            )
            return (
                f"{variables} {style.COLON} "
                f"{_indent(pretty(type, style=style), ' ' * (len(variables) + 3))}"
            )

        case AST.NoOp():
            return style.NOOP

        case AST.Continue(loop_label):
            return f"{style.CONTINUE} {style.label(loop_label.identifier)}"

        case AST.Break(loop_label):
            return f"{style.BREAK} {style.label(loop_label.identifier)}"

        case AST.Block(statements):
            if statements:
                statements = f"{style.SEMI}\n  ".join(
                    _indent(pretty(statement, style=style), '  ')
                    for statement in statements
                )
                return f"{style.LBRACE}\n  {statements}\n{style.RBRACE}"
            else:
                return f"{style.LBRACE}{style.RBRACE}"

        case AST.Loop(label, body):
            return f"{style.LOOP} {pretty(label, style=style)} {pretty(body, style=style)}"

        case AST.If(condition, truthy, falsey):
            return (
                f"{style.IF} {pretty(condition, style=style)}\n"
                f"{style.THEN} {pretty(truthy, style=style)}\n"
                f"{style.ELSE} {pretty(falsey, style=style)}"
            )

        case CFG.Assignment(variables, expression) | AST.Assignment(variables, expression):
            variables = f"{style.COMMA} ".join(
                pretty(variable, style=style)
                for variable in variables
            )
            return (
                f"{variables} {style.LARROW} "
                f"{_indent(pretty(expression, style=style), ' ' * (len(variables) + 4))}"
            )

        case CFG.Graph(entry_label, blocks):
            blocks = (
                '\n' * (0 < len(blocks)) +
                indent('\n\n'.join(
                    pretty(block, style=style)
                    for block in blocks
                ), ' '*18) +
                ('\n' + ' '*16) * (0 < len(blocks))
            )
            return (
                f"{style.LBRACE}\n"
                f"  {style.ENTRYPOINT} {style.label(entry_label.identifier)}"
                f"{blocks}\n"
                f"{style.RBRACE}"
            )

        case CFG.Block(block_label, action, terminals):
            action = _indent(pretty(action), ' ' * 18)
            terminals = _indent('\n'.join(
                pretty(terminal, style=style)
                for terminal in terminals
            ), ' '*18)

            return dedent(f"""
                {style.BLOCK} {style.label(block_label.identifier)} {style.LBRACE}
                  {action}{('\n' + ' ' * 18) * bool(action)}{terminals}
                {style.RBRACE}
            """)[1:-1]

        case CFG.Nothing():
            return ""

        case CFG.Wait(handle, variables):
            handle = style.label(handle.identifier)
            variables = f"{style.COMMA} ".join(
                pretty(variable, style=style)
                for variable in variables
            )
            return f"{style.WAIT} {handle} {style.ON} {variables}"

        case CFG.Assignments(assignments):
            return '\n'.join(
                pretty(assignment, style=style)
                for assignment in assignments
            )

        case CFG.Terminal(type, truthy_vars, falsey_vars):
            predicate = f" {style.AND} ".join(chain(
                (                  pretty(var, style=style) for var in truthy_vars),
                (f"{style.NOT} " + pretty(var, style=style) for var in falsey_vars),
            ))
            if predicate:
                predicate = f" {style.WHERE} {predicate}"
            return pretty(type, style=style) + predicate

        case CFG.Return(variables):
            variables = f"{style.COMMA} ".join(
                pretty(variable, style=style)
                for variable in variables
            )
            return f"{style.RETURN} {variables}"

        case CFG.Jump(target):
            target = style.label(target.identifier)
            return f"{style.JUMP} {target}"

        case CFG.GoTo(target):
            target = style.label(target.identifier)
            return f"{style.GOTO} {target}"

        case CFG.Call(handle, target, arguments):
            target = style.label(target.identifier)
            handle = style.label(handle.identifier)
            arguments = f"{style.COMMA} ".join(
                pretty(argument, style=style)
                for argument in arguments
            )
            return f"{style.CALL} {target}{style.LPAREN}{arguments}{style.RPAREN} {style.AS} {handle}"

        case _:
            raise TypeError(f"Can't format {node!r}.")
