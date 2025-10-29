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
    CFP.Start: "style = filled, fillcolor = cornflowerblue, color = white, fontcolor = white",
    CFP.Let: "style = filled, fillcolor = royalblue, color = white, fontcolor = white",
    CFP.Emit: "style = filled, fillcolor = navy, color = white, fontcolor = white",
    CFP.Merge: "style = filled, fillcolor = yellowgreen, color = white, fontcolor = white",
    CFP.Where: "style = filled, fillcolor = forestgreen, color = white, fontcolor = white",
    CFP.WhereNot: "style = filled, fillcolor = darkgreen, color = white, fontcolor = white",
    CFP.GoTo: "style = filled, fillcolor = darkorange, color = white, fontcolor = white",
    CFP.Fork: "style = filled, fillcolor = darkorchid, color = white, fontcolor = white",
    CFP.Gather: "style = filled, fillcolor = darkmagenta, color = white, fontcolor = white",
    CFP.SiblingProbe: "style = filled, fillcolor = rebeccapurple, color = white, fontcolor = white",
}


def render[A](graph: CFP.Graph, *, font: str = "monospace") -> str:
    nodes = (
        NODE_TEMPLATE.format(
            label=label.identifier,
            body=(
                f"{{{
                    pretty(node)
                    .replace('\\', '\\\\')
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
        for source, targets in graph.direct_edges.items()
        for target in targets
    )

    return PRORGAM_TEMPLATE.format(
        nodes="\n".join(nodes), edges="\n".join(edges), font=font
    )
