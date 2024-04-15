from typing import Any

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
{subgraphs}
{edges}
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


def render(
    program: common.Program[Any, CFG.Graph],
    *,
    font: str = "monospace"
) -> str:
    subgraphs = []
    edges = []

    for function in program.function_list:
        nodes = []

        for block in function.body.blocks.values():
            for terminal in block.terminals:
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

                edges.append(f'"{block.label.identifier}":s -> "{target}":n [{style}];')

            if isinstance(block.action, CFG.Waits):
                edges.append(
                    f'"{block.label.identifier}":s -> "{block.label.identifier}":n '
                    f'[{WAIT_STYLE.format(handle=",".join(
                        wait.handle.identifier
                        for wait in block.action.waits)
                    )}];'
                )

            nodes.append(
                NODE_TEMPLATE.format(
                    label=block.label.identifier,
                    body=pretty(block).replace("\n", "\\l"),
                )
            )

        subgraphs.append(
             FUNCTION_TEMPLATE.format(
                name=function.name.identifier,
                parameters=", ".join(
                    f"{name.identifier}: {type.source}"
                    for name, type in function.parameters.items()
                ),
                return_types=", ".join(
                    type.source
                    for type in function.return_types
                ),
                body="\n".join(nodes)
            )
        )

    return PRORGAM_TEMPLATE.format(
        subgraphs="\n".join(subgraphs),
        edges="\n".join(edges),
        font=font
    )
