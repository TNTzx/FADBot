"""Artist query object."""


import asyncio
import requests as req

import nextcord as nx

from .. import api
from . import artist
from . import exceptions as a_exc


class ArtistQuery():
    """Artist query."""
    def __init__(self, artists: list[artist.Artist] = None):
        self.artists = artists


    @classmethod
    def from_vadb_search(cls, search_term: str):
        """Creates an `ArtistQuery` from a search term."""
        try:
            response = api.make_request(api.Endpoints.artist_search(search_term)).json()["data"]
        except req.exceptions.HTTPError as exc:
            raise a_exc.VADBNoSearchResult(search_term) from exc


        async def from_vadb_data(artist_data: dict):
            """From VADB data, but async."""
            return artist.Artist.from_vadb_data(artist_data)

        async def gather():
            return await asyncio.gather(*[from_vadb_data(artist_data) for artist_data in response])
        return cls(
            artists = asyncio.run(gather())
        )
