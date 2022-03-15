"""Aliases."""


import backend.utils.new_dataclass as dt

from .. import artist_struct as a_s


class Alias(dt.Dataclass):
    """Stores an alias."""
    def __init__(self, name: str | None = None) -> None:
        self.name = name


class Aliases(a_s.ArtistStruct):
    """Stores a list of aliases."""
    def __init__(self, aliases: list[Alias] | None = None):
        self.aliases = aliases
