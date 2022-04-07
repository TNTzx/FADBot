"""Aliases."""


import backend.other.dataclass as dt

from ... import artist_struct


class Alias(artist_struct.ArtistStruct):
    """Stores an alias."""
    def __init__(self, name: str | None = None) -> None:
        self.name = name


    def vadb_to_edit_json(self) -> dict | list:
        return {"name": self.name}


    def firebase_to_json(self):
        return self.vadb_to_edit_json()

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        return cls(
            name = json.get("name")
        )


class Aliases(artist_struct.ArtistStruct):
    """Stores a list of aliases."""
    def __init__(self, aliases: list[Alias] | None = None):
        self.aliases = aliases


    def vadb_to_edit_json(self) -> dict | list:
        if self.aliases is None:
            return None

        return [alias.vadb_to_edit_json() for alias in self.aliases]


    def firebase_to_json(self):
        if self.aliases is None:
            return None

        return [alias.firebase_to_json() for alias in self.aliases]

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        if json is None:
            return cls()

        return cls(
            aliases = [
                Alias.firebase_from_json(alias_json) for alias_json in json
            ]
        )
