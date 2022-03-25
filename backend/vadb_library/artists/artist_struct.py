"""Contains a class for artist structures."""


import typing as typ

import backend.utils.new_dataclass as dt


class ArtistStruct(dt.Dataclass):
    """Parent class for artist structures."""
    # def get_json_dict(self):
    #     """Turns the data into a dictionary for sending."""
    #     data: dict = self.to_one_obj()
    #     for key, value in data.items():
    #         if isinstance(value, dict):
    #             data[key] = str(value)

    #     return data

    def vadb_to_create_json(self) -> dict | list:
        """Creates a JSON from this `ArtistStruct` for use in creating an artist in VADB."""

    def vadb_to_edit_json(self) -> dict | list:
        """Creates a JSON from this `ArtistStruct` for use in editing an artist in VADB."""

    def vadb_to_delete_json(self) -> dict | list:
        """Creates a JSON from this `ArtistStruct` for use in deleting an artist in VADB."""

    @classmethod
    def vadb_from_get_json(cls, json: dict | list) -> None:
        """Creates an `ArtistStruct` from the JSON received from VADB."""
