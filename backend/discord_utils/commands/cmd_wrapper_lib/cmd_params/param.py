"""Contains information about a parameter."""


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


class ParamOptional(param_struct.ParamWrapper):
    """An optional parameter."""
    def get_syntax(self) -> str:
        return f"[{self.param_unit.get_syntax()}]"
