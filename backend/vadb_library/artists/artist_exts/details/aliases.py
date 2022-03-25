"""Aliases."""


import backend.utils.new_dataclass as dt

from ... import artist_struct


class Alias(artist_struct.ArtistStruct):
    """Stores an alias."""
    def __init__(self, name: str | None = None) -> None:
        self.name = name


    def vadb_to_edit_json(self) -> dict | list:
        return {"name": self.name}


class Aliases(artist_struct.ArtistStruct):
    """Stores a list of aliases."""
    def __init__(self, aliases: list[Alias] | None = None):
        self.aliases = aliases


    def vadb_to_edit_json(self) -> dict | list:
        if self.aliases is None:
            return None

        return [alias.vadb_to_edit_json() for alias in self.aliases]
