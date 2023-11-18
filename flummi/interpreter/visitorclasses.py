from abc import ABC, abstractmethod

from ..grammars import proc, common

class Visitor(ABC):

    @abstractmethod
    def visit(self, variable: common.Variable):
        ...

class InterpretVisitor(Visitor):
   
   def  visit(self, assignment: proc.Assignment):
       return assignment.expression                     #herrausfinden wie man Expressions mit DuckDB auswertet