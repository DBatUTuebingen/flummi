from typing import TypeVar

from ..grammars import proc, common
from .. import parser

E = TypeVar("E", bound=common.SupportsFormat)
T = TypeVar("T", bound=common.SupportsStr)

__all__ = (
    "interpret"
)

def interpret(program: proc.Program[E, T]):
    ...
    """
    go through all nodes
    depending on node do: (visitor pattern) 
    """ 