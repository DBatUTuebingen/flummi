from typing import Callable

from ..IR import CFP
from ..library.sql import SQL

type frontend = Callable[[str], CFP.Program]

type backend = Callable[[CFP.Program], SQL]

type compiler = Callable[[str], SQL]
