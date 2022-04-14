"""Artist query object."""


import requests as req

from .. import queries
from .. import excepts
from .. import api
from . import artist


class ArtistQuery(queries.BaseQuery):
    """Artist query."""
    @classmethod
    def from_search(cls, search_term: str):
        """Creates an `ArtistQuery` from a search term."""
        try:
            response = api.make_request(api.Endpoints.artist_search(search_term)).json()
        except req.exceptions.HTTPError as exc:
            raise excepts.VADBNoSearchResult(search_term) from exc

        return cls(
            artists = [
                artist.Artist.vadb_from_get_json(artist_data)
                for artist_data in response["data"]
            ]
        )
