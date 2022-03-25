"""Usage rights."""


import backend.utils.new_dataclass as dt

from ... import artist_struct


class UsageRight(artist_struct.ArtistStruct):
    """Defines a usage right."""
    def __init__(
            self,
            description: str | None = None,
            is_verified: bool = True
            ):
        self.description = description
        self.is_verified = is_verified


    def vadb_to_edit_json(self) -> dict | list:
        return {
            "name": self.description,
            "value": self.is_verified
        }


class UsageRights(artist_struct.ArtistStruct):
    """Defines a list of usage rights."""
    def __init__(self, usage_rights: list[UsageRight] | None = None):
        self.usage_rights = usage_rights


    def vadb_to_edit_json(self) -> dict | list:
        return [usage_right.vadb_to_edit_json() for usage_right in self.usage_rights]
