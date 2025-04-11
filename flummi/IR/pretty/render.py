from .. import CFG
from .pretty import pretty


__all__ = (
    "render",
)


PRORGAM_TEMPLATE= """\
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

NODE_STYLES: dict[type[CFG.Node], str] = {
    CFG.Pop:      'style = filled, fillcolor = orange         , color = white, fontcolor = white',
    CFG.Push:     'style = filled, fillcolor = goldenrod      , color = white, fontcolor = white',
    CFG.Where:    'style = filled, fillcolor = forestgreen    , color = white, fontcolor = white',
    CFG.WhereNot: 'style = filled, fillcolor = forestgreen    , color = white, fontcolor = white',
    CFG.Merge:    'style = filled, fillcolor = darkcyan       , color = white, fontcolor = white',
    CFG.Let:      'style = filled, fillcolor = royalblue      , color = white, fontcolor = white',
    CFG.Emit:     'style = filled, fillcolor = navy           , color = white, fontcolor = white',
    CFG.Link:     'style = filled, fillcolor = firebrick      , color = white, fontcolor = white',
    CFG.Resume:   'style = filled, fillcolor = crimson        , color = white, fontcolor = white',
    CFG.Lookup:   'style = filled, fillcolor = purple         , color = white, fontcolor = white',
    CFG.Memoize:  'style = filled, fillcolor = mediumvioletred, color = white, fontcolor = white',
}

def render(
    graph: CFG.Graph,
    *,
    font: str = "monospace"
) -> str:
    nodes = (
        NODE_TEMPLATE.format(
            label=label.identifier,
            body=(
                f"{{{
                    pretty(node)
                    .replace("\n", "\\l")
                    .replace("|", "\\|")
                    .replace(" ", "\\ ")
                    .replace("{", "\\{")
                    .replace("}", "\\}")
                    .replace("<", "\\<")
                    .replace(">", "\\>")
                    .replace("\"", "\\\"")
                }\\l|{{{label.identifier}\\l|@{label.annotation.column}:{label.annotation.line}}}}}"
            ),
            style=NODE_STYLES.get(type(node), '')
        )
        for label, node in graph.nodes.items()
    )

    edges = []

    edges.extend(
        f'"{source.identifier}":s -> "{target.identifier}":n;'
        for source, targets in graph.edges.items()
        for target in targets
    )

    edges.extend(
        f'"{sink.identifier}":s -> "{source.identifier}":n [style="dashed"];'
        for sink, sink_node in graph.nodes.items()
        if isinstance(sink_node, CFG.Push)
        for source, source_node in graph.nodes.items()
        if isinstance(source_node, CFG.Pop)
        and sink_node.label == source_node.label
    )


    return PRORGAM_TEMPLATE.format(
        nodes="\n".join(nodes),
        edges="\n".join(edges),
        font=font
    )
