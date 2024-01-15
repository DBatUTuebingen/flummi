from itertools import chain

from .. import CFG
from .print import pretty, STYLE


TEMPLATE= """\
digraph "%cfg%" {{
  node [
    shape=rectangle,
    nojustify=true,
    penwidth=2,
    style="rounded,filled",
    fontcolor="#5C6166",
    fontname = "{font}",
  ];
  graph [
    fontname = "{font}",
    splines=ortho
  ];
  edge [
    fontname = "{font}",
    penwidth=2,
    color="#FA8D3E"
  ];
  subgraph "%cfg%" {{
    cluster=true;
    style="rounded,dotted";
    color="#5C6166";
    node [
      fillcolor="#DDF0F6",
      color="#55B4D4"
    ];
    edge [
      color="#FA8D3E"
    ];
    {nodes}
    {edges}
  }}
  subgraph "%inputs%" {{
    node [
      fillcolor="#F6F2F9",
      color="#A37ACC";
    ];
    edge [
      color="#A37ACC",
      style="dashed"
    ];
    "%inputs%" -> "{root}";
  }}
}}
"""

NODE_TEMPLATE = '"{label}" [label="{body}\\l"];'


def dot(graph: CFG.Graph, font: str = "PragmataPro") -> str:
    STYLE.off()
    nodes = "\n    ".join(
        NODE_TEMPLATE.format(
            label=label.label,
            body=pretty(block).replace("\n", "\\l"),
        )
        for label, block in graph.blocks.items()
    )
    edges = "\n    ".join(chain.from_iterable(
        (
          f'"{label.label}" -> "{successor.label}" [style="{["solid", "dashed"][successor in CFG.jumps(block)]}"];'
          for successor in CFG.successors(block)
        )
        for label, block in graph.blocks.items()
    ))
    STYLE.on()
    return TEMPLATE.format(
        font=font,
        nodes=nodes,
        edges=edges,
        inputs="",
        root=graph.entry_label.label,
    )
