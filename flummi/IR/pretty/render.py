from typing import Any

from .. import CFG, common
from .pretty import pretty
from ...library import errors


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


def render(
    program: common.Program[Any, CFG.Graph[errors.Location]],
    *,
    font: str = "monospace"
) -> str:
    subgraphs = []
    edges = []

    for function in program.function_list:
        nodes = (
            NODE_TEMPLATE.format(
                label=label.identifier,
                body="\\l".join((
                    pretty(node).replace("\n", "\\l"),
                    f"@{label.annotation.column}:{label.annotation.line}"
                ))
            )
            for label, node in function.body.nodes.items()
        )

        edges = (
            f'"{source.identifier}":s -> "{target.identifier}":n;'
            for source, targets in function.body.edges.items()
            for target in targets
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
