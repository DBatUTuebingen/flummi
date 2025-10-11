from .. import CFP
from ...compiler import lowering
from .pretty import pretty


__all__ = ("render",)


PRORGAM_TEMPLATE = """\
digraph "program" {{
node [
    shape = Mrecord,
    nojustify = true,
    fontname = "{font}",
];
graph [
    fontname = "{font}",
];
edge [
    fontname = "{font}",
];
{nodes}
{edges}
}}
"""

NODE_TEMPLATE = '"{label}" [label="{body}",{style}];'

NODE_STYLES: dict[type[lowering.Node], str] = {
    CFP.Let: "style = filled, fillcolor = royalblue, color = white, fontcolor = white",
    CFP.Emit: "style = filled, fillcolor = navy, color = white, fontcolor = white",
}


def render[A](graph: lowering.Graph, *, font: str = "monospace") -> str:
    nodes = (
        NODE_TEMPLATE.format(
            label=label.identifier,
            body=(
                f"{{{
                    pretty(node)
                    .replace('\n', '\\l')
                    .replace('|', '\\|')
                    .replace(' ', '\\ ')
                    .replace('{', '\\{')
                    .replace('}', '\\}')
                    .replace('<', '\\<')
                    .replace('>', '\\>')
                    .replace('"', '\\"')
                }\\l|{{{label.identifier}\\l|@{label.annotation.column}:{
                    label.annotation.line
                }}}}}"
            ),
            style=NODE_STYLES.get(type(node), ""),
        )
        for label, node in graph.nodes.items()
    )

    edges: list[str] = []

    edges.extend(
        f'"{source.identifier}":s -> "{target.identifier}":n;'
        for source, targets in graph.edges.items()
        for target in targets
    )

    return PRORGAM_TEMPLATE.format(
        nodes="\n".join(nodes), edges="\n".join(edges), font=font
    )
