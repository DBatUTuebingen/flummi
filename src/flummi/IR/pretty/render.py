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
    CFP.Stop: "style = filled, fillcolor = gray3, color = white, fontcolor = white",
    CFP.Start: "style = filled, fillcolor = cornflowerblue, color = white, fontcolor = white",
    CFP.Assignment: "style = filled, fillcolor = royalblue, color = white, fontcolor = white",
    CFP.Emit: "style = filled, fillcolor = navy, color = white, fontcolor = white",
    CFP.Where: "style = filled, fillcolor = forestgreen, color = white, fontcolor = white",
    CFP.Merge: "style = filled, fillcolor = olive, color = white, fontcolor = white",
    CFP.Jump: "style = filled, fillcolor = darkorange, color = white, fontcolor = white",
    CFP.Fork: "style = filled, fillcolor = darkviolet, color = white, fontcolor = white",
    CFP.Gather: "style = filled, fillcolor = maroon4, color = white, fontcolor = white",
    CFP.IsSynced: "style = filled, fillcolor = indigo, color = white, fontcolor = white",
}


def render[A](graph: CFP.Plan, *, font: str = "monospace") -> str:
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
                }\\l|{{{label.identifier}\\l|@{
                    f'{label.location.column}:{label.location.line}'
                    if label.location is not None
                    else '<unknown>'
                }}}}}"
            ),
            style=NODE_STYLES.get(type(node), ""),
        )
        for label, node in graph.primitives.items()
    )

    edges: list[str] = []

    edges.extend(
        f'"{source.identifier}":s -> "{target.identifier}":n;'
        for source, targets in graph.successors_of.items()
        for target in targets
    )

    edges.extend(
        f'"{label.identifier}":s -> "{primitive.label.identifier}":n;'
        for label, primitive in graph.primitives.items()
        if isinstance(primitive, CFP.Jump)
    )

    return PRORGAM_TEMPLATE.format(
        nodes="\n".join(nodes), edges="\n".join(edges), font=font
    )
