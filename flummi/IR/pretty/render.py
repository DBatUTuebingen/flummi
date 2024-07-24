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
    shape = Mrecord,
    nojustify = true,
    fontname = "{font}",
];
graph [
    fontname = "{font}"
];
edge [
    fontname = "{font}",
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

NODE_TEMPLATE = '"{label}" [label="{body}",{style}];'

NODE_STYLES: dict[type[CFG.Node], str] = {
    CFG.Source:      'color = forestgreen    , fontcolor = forestgreen    ',
    CFG.Sink:        'color = firebrick      , fontcolor = firebrick      ',
    CFG.Join:        'color = goldenrod      , fontcolor = goldenrod      ',
    CFG.Fork:        'color = purple         , fontcolor = purple         ',
    CFG.Wait:        'color = orange         , fontcolor = orange         ',
    CFG.Mark:        'color = royalblue      , fontcolor = royalblue      ',
    CFG.Conditional: 'color = mediumvioletred, fontcolor = mediumvioletred',
    CFG.Emit:        'color = darkcyan       , fontcolor = darkcyan       ',
    CFG.Merge:       'color = darkcyan       , fontcolor = darkcyan       ',
    CFG.Assignment:  'color = darkcyan       , fontcolor = darkcyan       ',
}

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
                body=(
                    f"{{{
                        pretty(node)
                        .replace("\n", "\\l")
                        .replace(" ", "\\ ")
                        .replace("{", "\\{")
                        .replace("}", "\\}")
                        .replace("<", "\\<")
                        .replace(">", "\\>")
                    }\\l|@{label.annotation.column}:{label.annotation.line}}}"
                ),
                style=NODE_STYLES.get(type(node), '')
            )
            for label, node in function.body.nodes.items()
        )

        edges.extend(
            f'"{source.identifier}":s -> "{target.identifier}":n;'
            for source, targets in function.body.edges.items()
            for target in targets
        )

        edges.extend(
            f'"{sink.identifier}":s -> "{source.identifier}":n [style="dashed"];'
            for sink, sink_node in function.body.nodes.items()
            if isinstance(sink_node, CFG.Sink)
            for source, source_node in function.body.nodes.items()
            if isinstance(source_node, CFG.Source)
            and sink_node.label == source_node.label
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
