"""Aliases."""


import backend.utils.new_dataclass as dt


class Alias(dt.Dataclass):
    """Stores an alias."""
    def __init__(self, name: str | None = None) -> None:
        self.name = name

    def __str__(self):
        return self.name

class Aliases(dt.Dataclass):
    """Stores a list of aliases."""
    def __init__(self, aliases: list[Alias] | None = None):
        self.aliases = aliases

    def __str__(self):
        if self.aliases is not None:
            return self.aliases
        else:
            return self.__repr__
