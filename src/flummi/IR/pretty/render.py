from .. import CFP
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

NODE_STYLES: dict[type[CFP.Primitive], str] = {
    CFP.Assignment: "style = filled, fillcolor = royalblue, color = white, fontcolor = white",
    CFP.Emit: "style = filled, fillcolor = navy, color = white, fontcolor = white",
}


def render[A](graph: CFP.Graph, *, font: str = "monospace") -> str:
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
                }\\l|{{{label.identifier}\\l|@{label.location.column}:{
                    label.location.line
                }}}}}"
            ),
            style=NODE_STYLES.get(type(node), ""),
        )
        for label, node in graph.primitives.items()
    )

    edges: list[str] = []

    edges.extend(
        f'"{source.identifier}":s -> "{target.identifier}":n;'
        for source, targets in graph.transitions.items()
        for target in targets
    )

    return PRORGAM_TEMPLATE.format(
        nodes="\n".join(nodes), edges="\n".join(edges), font=font
    )
