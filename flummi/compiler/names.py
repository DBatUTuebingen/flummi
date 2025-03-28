iteration: str = "@iteration"
label: str = "@label"
return_label: str = "@return_label"
kind: str = "@kind"
depth: str = "@depth"
max_depth: str = "@max_depth"

working_table: str = "@loop"

def register(r: int) -> str:
  return f"@register_{r}"
