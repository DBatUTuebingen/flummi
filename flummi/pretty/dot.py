from itertools import chain

from ..grammars import CFG
from ..algorithms import compute_successors, get_jumps, compute_depth_information
from .print import pretty, STYLE


TEMPLATE= """\
digraph "%pdg%" {{
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
    "%inputs%" [label="{inputs}\l"];
    "%inputs%" -> "{root}";
  }}
}}
"""

NODE_TEMPLATE = '"{label}" [label="{body}\l"];'


def dot(graph: CFG.Graph[str, str], font: str = "PragmataPro") -> str:
    STYLE.off()
    jumps = get_jumps(graph)
    nodes = "\n    ".join(
        NODE_TEMPLATE.format(
            label=label.label,
            body=pretty(block).replace("\n", "\\l"),
        )
        for label, block in graph.blocks.items()
    )
    edges = "\n    ".join(chain.from_iterable(
        (
          f'"{label.label}" -> "{successor.label}" [style="{["solid", "dashed"][(label,successor) in jumps]}"];'
          for successor in successors
        )
        for label, successors in compute_successors(graph).items()
    ))
    inputs = "\\l".join(
        f"{variable} <- {input!s}"
        for variable, input in graph.inputs.items()
    )
    # jumps = "\\l".join(
    #     pretty(jump).replace("\n", "\\l")
    #     for jump in graph.jumps
    # )
    # depths = compute_depth_information(graph)
    # jump_placement = f'{max(depths, key=depths.__getitem__).label} -> "%jumps%";'
    STYLE.on()
    return TEMPLATE.format(
        font=font,
        nodes=nodes,
        edges=edges,
        inputs=inputs,
        root=graph.entry_label.label,
        # jumps=jumps,
        # jump_placement=jump_placement
    )
