"""Exceptions."""


class VADBError(Exception):
    """A VADB error occurred."""


class VADBInvalidResponse(Exception):
    """An invalid response from VADB occurred."""

class VADBNoArtistID(VADBError):
    """No artist found with given ID."""
    def __init__(self, artist_id: int):
        super().__init__(f"No VADB entry with artist id {artist_id}.")
