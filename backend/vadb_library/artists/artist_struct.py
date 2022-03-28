"""Contains a class for artist structures."""


import typing as typ

import backend.firebase as firebase


class ArtistStruct(firebase.FBStruct):
    """Parent class for artist structures."""

    def vadb_to_create_json(self):
        """Creates a JSON from this `ArtistStruct` for use in creating an artist in VADB."""
        raise ValueError("\"vadb_to_create_json\" not supported for this ArtistStruct.")

    def vadb_to_edit_json(self):
        """Creates a JSON from this `ArtistStruct` for use in editing an artist in VADB."""
        raise ValueError("\"vadb_to_edit_json\" not supported for this ArtistStruct.")

    def vadb_to_delete_json(self):
        """Creates a JSON from this `ArtistStruct` for use in deleting an artist in VADB."""
        raise ValueError("\"vadb_to_create_json\" not supported for this ArtistStruct.")

    @classmethod
    def vadb_from_get_json(cls, json: dict | list) -> None:
        """Creates an `ArtistStruct` from the JSON received from VADB."""
        raise ValueError("\"vadb_from_get_json\" not supported for this ArtistStruct.")
