from itertools import chain

from . import CFG
from .pretty import pretty, STYLE


__all__ = (
    "render",
)


TEMPLATE= """\
digraph "%cfg%" {{
  node [
    shape = rectangle,
    nojustify = true,
    penwidth = 1.5,
    style="rounded",
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
  {nodes}
  {edges}
}}
"""

NODE_TEMPLATE = '"{label}" [label="{body}\\l"];'

JUMP_STYLE = 'style="dashed",color="#F7921D"'
GOTO_STYLE = 'style="solid",color="#0071BC"'
CALL_STYLE = 'style="dashed",color="#86B300"'
WAIT_STYLE = 'style="dotted",color="#A37ACC"'

def render(graph: CFG.Graph, font: str = "PragmataPro") -> str:
    STYLE.off()
    nodes, edges = [], []
    for label, block in graph.blocks.items():
        nodes.append(
          NODE_TEMPLATE.format(
              label=label.label,
              body=pretty(block).replace("\n", "\\l"),
          )
        )

        for other in CFG.gotos(block):
            edges.append(
                f'"{label.label}":s -> "{other.label}":n [{GOTO_STYLE}];'
            )

        for other in CFG.jumps(block):
            edges.append(
                f'"{label.label}":s -> "{other.label}":n [{JUMP_STYLE}];'
            )

        for other in CFG.calls(block):
            edges.append(
                f'"{label.label}":s -> "{other.label}":n [{CALL_STYLE}];'
            )

        if isinstance(block.action, CFG.Wait):
            edges.append(
                f'"{label.label}":s -> "{label.label}":n [{WAIT_STYLE}];'
            )

    STYLE.on()
    return TEMPLATE.format(
        font=font,
        nodes="\n  ".join(nodes),
        edges="\n  ".join(edges),
    )
