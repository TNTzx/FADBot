"""Contains information about a parameter."""


import backend.other as ot

from . import param_struct


class Param(param_struct.ParamUnit):
    """A parameter."""
    def __repr__(self) -> str:
        return f"({self.get_syntax()})"


class ParamArgument(Param):
    """A parameter that takes in a value."""
    def get_syntax(self) -> str:
        return f"<{self.name}>"

class ParamLiteral(Param):
    """A parameter with a literal value. Usually takes in a string."""
    def get_syntax(self) -> str:
        return f"\"{self.name}\""

    def get_syntax_arranged(self) -> str:
        return self.name


class ParamOptional(param_struct.ParamUnitWrapper):
    """An optional parameter."""
    def get_syntax(self) -> str:
        return f"[{self.param_unit.get_syntax()}]"


    def get_syntax_arranged(self) -> str:
        return f"[{self.param_unit.get_syntax_arranged()}]"


    def get_syntax_help(self, prefix: ot.Indent = ot.Indent()) -> str:
        old_syntax = super().get_syntax_help(prefix)
        return f"{old_syntax}(optional) {self.param_unit.description}"
