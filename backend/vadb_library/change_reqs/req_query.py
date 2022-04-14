"""Request query module."""


from .. import artist


class RequestQuery():
    """Represents a query for requests."""
    def __init__(self, artists: list[artist.Artist] = None):
        if len(artists) == 0:
            self.artists = None
        else:
            self.artists = artists


    @classmethod
    def from_search()
