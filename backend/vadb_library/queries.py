"""Contains the base class for queries."""


from . import artist_lib


class BaseQuery():
    """Base class for queries."""
    def __init__(self, artists: list[artist_lib.Artist] = None):
        if len(artists) == 0:
            self.artists = None
        else:
            self.artists = artists


    @classmethod
    def from_search(cls, search_term: str):
        """Returns a `BaseQuery` for this search term."""
