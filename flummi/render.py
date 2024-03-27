from itertools import chain

from .IR import AST, CFG, common
from .pretty import pretty


__all__ = (
    "render",
)


PRORGAM_TEMPLATE= """\
digraph "program" {{
node [
    shape = box,
    nojustify = true,
    fontname = "{font}",
    fontcolor = "#000",
    color = "#000",
];
graph [
    fontname = "{font}"
];
edge [
    fontname = "{font}",
    penwidth = 1.5,
];
{functions}
}}
"""

FUNCTION_TEMPLATE= """\
subgraph "func%{name}" {{
cluster=true;
{body}
label="{name}({parameters}) -> {return_types}"
}}
"""

NODE_TEMPLATE = '"{label}" [label="{body}\\l"];'

JUMP_STYLE = 'style="dashed",color="#F7921D"'
GOTO_STYLE = 'style="solid",color="#0071BC"'
CALL_STYLE = 'style="dashed",color="#86B300",label="{handle}"'
WAIT_STYLE = 'style="dotted",color="#A37ACC",label="{handle}"'


def render(thing, *, font: str = "monospace") -> str:
    match thing:
        case common.Program(main_function_name, inputs, function_list):
            functions = "\n".join(
                render(function, font=font)
                for function in function_list
            )

            return PRORGAM_TEMPLATE.format(functions=functions, font=font)

        case common.Function(name, parameters, return_types, body):
            body = render(body, font=font)

            return FUNCTION_TEMPLATE.format(
                name=name.identifier,
                parameters=", ".join(
                    f"{name.identifier}: {type.source}"
                    for name, type in parameters.items()
                ),
                return_types=", ".join(
                    type.source
                    for type in return_types
                ),
                body=body
            )

        case CFG.Graph(_, blocks):
            return "\n".join(
                render(block, font=font)
                for block in blocks.values()
            )

        case CFG.Block(label, action, terminals):
            edges = []

            for terminal in terminals:
                match terminal.type:
                    case CFG.GoTo(target):
                        style = GOTO_STYLE
                        target = target.identifier
                    case CFG.Jump(target):
                        style = JUMP_STYLE
                        target = target.identifier
                    case CFG.Call(handle, target, _):
                        style = CALL_STYLE.format(handle=handle.identifier)
                        target = target.identifier
                    case _:
                        continue

                edges.append(f'"{label.identifier}":s -> "{target}":n [{style}];')

            if isinstance(action, CFG.Wait):
                edges.append(
                    f'"{label.identifier}":s -> "{label.identifier}":n '
                    f'[{WAIT_STYLE.format(handle=action.handle.identifier)}];'
                )

            return (
                NODE_TEMPLATE.format(
                    label=label.identifier,
                    body=pretty(thing).replace("\n", "\\l"),
                ) + "\n" + "\n".join(edges)
            )

        case _:
            return ""
