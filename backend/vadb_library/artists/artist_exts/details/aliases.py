"""Aliases."""


import backend.utils.new_dataclass as dt

from ... import artist_struct


class Alias(dt.Dataclass):
    """Stores an alias."""
    def __init__(self, name: str | None = None) -> None:
        self.name = name


class Aliases(artist_struct.ArtistStruct):
    """Stores a list of aliases."""
    def __init__(self, aliases: list[Alias] | None = None):
        self.aliases = aliases
