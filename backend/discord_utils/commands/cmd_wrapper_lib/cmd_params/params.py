"""Contains information about parameters."""


from __future__ import annotations

from . import param_struct as prm_struct
from . import param as prm


class Params(prm_struct.ParamList):
    """A list of parameters."""
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.params})"


    def __add__(self, other: Params):
        return Params(
            *(
                list(self.params) + list(other.params)
            ),
            description = self.description
        )


    def get_syntax(self) -> str:
        return " ".join([param.get_syntax() for param in self.params])

    def get_syntax_arranged(self) -> str:
        return " ".join([param.get_syntax_arranged() for param in self.params])


    def _get_one_start_slice(self):
        """Gets `self.params[1:].`"""
        return Params(*(self.params[1:]), description = self.description)


    def get_all_arrangements(self):
        """Gets all possible arrangements of the parameters."""
        if len(self.params) == 0:
            return [Params(description = self.description)]

        all_combs = []
        if isinstance(self.params[0], ParamsSplit):
            for params_from_split in self.params[0].params:
                for param_from_split in params_from_split.get_all_arrangements():
                    for next_param_comb in self._get_one_start_slice().get_all_arrangements():
                        all_combs.append(param_from_split + next_param_comb)
        else:
            for next_param_comb in self._get_one_start_slice().get_all_arrangements():
                all_combs.append(
                    Params(self.params[0], description = self.description) + next_param_comb
                )

        return all_combs


    def has_splits(self):
        """Returns `True` if a `ParamsSplit` is found in this `Params`."""
        for param in self.params:
            if isinstance(param, ParamsSplit):
                return True

        return False


class ParamsSplit(prm_struct.ParamNest):
    """Denotes a split in the parameters."""
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.params})"


    def get_syntax(self) -> str:
        formatted = " | ".join([param.get_syntax() for param in self.params])
        return f"< {formatted} >"
