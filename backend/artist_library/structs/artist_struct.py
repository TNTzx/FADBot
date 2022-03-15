"""Contains a class for artist structures."""


import abc

import backend.utils.new_dataclass as dt


class ArtistStruct(dt.Dataclass, abc.ABC):
    """Parent class for artist structures."""
    # def get_json_dict(self):
    #     """Turns the data into a dictionary for sending."""
    #     data: dict = self.to_one_obj()
    #     for key, value in data.items():
    #         if isinstance(value, dict):
    #             data[key] = str(value)

    #     return data

    @classmethod
    @abc.abstractmethod
    def from_vadb_receive(cls, response: dict) -> None:
        """Returns an object from this class from VADB's response."""


class ArtistStructVADBCreate(ArtistStruct):
    """Parent class for those that need an implementation of creating a VADB artist."""
    @abc.abstractmethod
    def to_vadb_create(self) -> dict | list:
        """Returns a `dict` or a `list` for creating a VADB artist."""

class ArtistStructVADBEdit(ArtistStruct):
    """Parent class for those that need an implementation of editing a VADB artist."""
    @abc.abstractmethod
    def to_vadb_edit(self) -> dict | list:
        """Returns a `dict` or a `list` for editing a VADB artist."""

class ArtistStructVADBDelete(ArtistStruct):
    """Parent class for those that need an implementation of deleting a VADB artist."""
    @abc.abstractmethod
    def to_vadb_delete(self) -> dict | list:
        """Returns a `dict` or a `list` for deleting a VADB artist."""
