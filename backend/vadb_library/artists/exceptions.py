"""Exceptions."""


class VADBError(Exception):
    """A VADB error occurred."""


class VADBInvalidResponse(VADBError):
    """An invalid response from VADB occurred."""

class VADBNoArtistID(VADBError):
    """No artist found with given ID."""
    def __init__(self, artist_id: int):
        super().__init__(f"No VADB entry with artist id {artist_id}.")

class VADBNoSearchResult(VADBError):
    """No search result for query."""
    def __init__(self, search_term: str):
        super().__init__(f"No artist in VADB matching search term \"{search_term}\".")
