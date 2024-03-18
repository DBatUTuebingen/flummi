from itertools import chain

from . import CFG
from .pretty import pretty, STYLE


__all__ = (
    "render",
)


TEMPLATE= """\
digraph "%cfg%" {{
  node [
    shape=rectangle,
    nojustify=true,
    penwidth=2,
    style="rounded",
    fontname = "{font}",
    fontcolor="#000",
    color="#000",
  ];
  graph [
    fontname = "{font}",
    splines=ortho
  ];
  edge [
    fontname = "{font}",
    penwidth=2,
  ];
  {nodes}
  {edges}
}}
"""

NODE_TEMPLATE = '"{label}" [label="{body}\\l"];'

JUMP_STYLE = 'style="dashed",color="#F7921D"'
GOTO_STYLE = 'style="solid",color="#0071BC"'

def render(graph: CFG.Graph, font: str = "PragmataPro") -> str:
    STYLE.off()
    nodes = "\n  ".join(
        NODE_TEMPLATE.format(
            label=label.label,
            body=pretty(block).replace("\n", "\\l"),
        )
        for label, block in graph.blocks.items()
    )
    edges = "\n  ".join(chain.from_iterable(
        (
          f'"{label.label}" -> "{successor.label}" [{[GOTO_STYLE, JUMP_STYLE][successor in CFG.jumps(block)]}];'
          for successor in CFG.successors(block)
        )
        for label, block in graph.blocks.items()
    ))
    STYLE.on()
    return TEMPLATE.format(
        font=font,
        nodes=nodes,
        edges=edges,
    )
