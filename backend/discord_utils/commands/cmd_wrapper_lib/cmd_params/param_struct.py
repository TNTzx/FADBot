"""Contains the parent class for all parameter-related information."""


from __future__ import annotations

import copy

from . import prefixes


class ParamStruct():
    """Parent class for all parameter structures."""
    def get_syntax(self) -> str:
        """Gets the formatted version of this `ParamStruct`."""

    def get_syntax_arranged(self) -> str:
        """Gets the syntax for arranged of this `ParamStruct`."""
        return self.get_syntax()

    def get_syntax_help(self, prefix: prefixes.Indent = prefixes.Indent()) -> str:
        """Gets the syntax help of this `ParamStruct`."""


class ParamUnit(ParamStruct):
    """Parent class for all unit parameters, like `ParamLiteral`."""
    def __init__(self, name: str, *, description: str):
        self.name = name
        self.description = description


    def get_syntax_help(self, prefix: prefixes.Indent = prefixes.Indent()) -> str:
        return f"{prefix.get_str()}{self.get_syntax()}: {self.description}"


class ParamWrapper(ParamStruct):
    """Parent class that wraps around a `ParamUnit`, like `ParamOptional`."""
    def __init__(self, param_unit: ParamUnit):
        self.param_unit = param_unit


class ParamList(ParamStruct):
    """Parent class for all list parameters, like `Params`."""
    def __init__(self, *params: ParamUnit | ParamList, description: str = None):
        self.params = params
        self.description = description


    def get_syntax_help(self, prefix: prefixes.Indent = prefixes.Indent()) -> str:
        new_prefix = copy.deepcopy(prefix)
        new_prefix.level += 1


        params_syntax_help = []
        for param in self.params:
            if issubclass(param.__class__, ParamList):
                if len(param.params) == 1:
                    params_syntax_help.append(param.params[0].get_syntax_help(new_prefix))
                    continue

            params_syntax_help.append(param.get_syntax_help(new_prefix))

        params_syntax_help = "\n".join(params_syntax_help)

        return (
            f"{prefix.get_str()}{self.get_syntax()}: {self.description if self.description is not None else ''}\n"
            f"{params_syntax_help}"
        )


    def get_all_arrangements(self):
        """Gets all arrangements for this `ParamList`."""


class ParamNest(ParamList):
    """Parent class for nesting parameters, like `ParamsSplit`."""
    def __init__(self, *params: ParamList, description: str = None):
        if description is None:
            raise ValueError("No description provided for this ParamNest.")

        for param in params:
            if not issubclass(param.__class__, ParamList):
                raise ValueError(f"Param {param} not a ParamList.")

        self.params = params
        self.description = description
