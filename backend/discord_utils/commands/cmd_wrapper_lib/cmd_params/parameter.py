"""Contains information about a parameter."""


from . import param_struct


class Param(param_struct.ParamStruct):
    """A parameter."""
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"({self.get_formatted()})"


    def get_formatted(self) -> str:
        """Gets the formatted version of this `Param`."""


# TODO get_formatted
class ParamArgument(Param):
    """A parameter that takes in a value."""

class ParamLiteral(Param):
    """A parameter with a literal value. Usually takes in a string."""
