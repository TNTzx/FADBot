"""Contains information about parameters."""


from __future__ import annotations

from . import param_struct as prm_struct
from . import param as prm


class Params(prm_struct.ParamStruct):
    """A list of parameters."""
    def __init__(self, *params_list: prm_struct.ParamStruct | prm.Param | ParamsSplit | list):
        self.params = params_list

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.params})"


    def __add__(self, other: Params):
        return Params(
            tuple(
                list(self.params) + list(other.params)
            )
        )


    def get_formatted(self) -> str:
        formatted = ", ".join([param.get_formatted() for param in self.params])
        return f"|{formatted}|"


    def _get_one_start_slice(self):
        """Gets `self.params[1:].`"""
        return Params(self.params[1:])


    def get_all_arrangements(self):
        """Gets all possible arrangements of the parameters."""
        if len(self.params) == 0:
            return [Params()]

        all_combs = []
        if isinstance(self.params[0], ParamsSplit):
            for params_from_split in self.params[0].params_split:
                for param_from_split in params_from_split.get_all_arrangements():
                    for next_param_comb in self._get_one_start_slice().get_all_arrangements():
                        all_combs.append(
                            Params(
                                param_from_split + next_param_comb
                            )
                        )
        else:
            for next_param_comb in self._get_one_start_slice().get_all_arrangements():
                all_combs.append(
                    Params(self.params[0]) + next_param_comb
                )

        return all_combs


class ParamsSplit(prm_struct.ParamStruct):
    """Denotes a split in the parameters."""
    def __init__(self, *params_split: prm_struct.ParamStruct | Params):
        self.params_split = params_split

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.params_split})"


    def get_formatted(self) -> str:
        formatted = ", ".join([param.get_formatted() for param in self.params_split])
        return f"[{formatted}]"
