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

    def generate_embed(self,
            title: str = None,
            description: str = None
            ):
        """Generates an embed for multiple artists."""
        embed = nx.Embed(
            color = 0xFF0000,
            title = title,
            description = description
        )
    

    @classmethod
    def from_vadb_search(cls, search_term: str):
        """Returns a list of `Artist`s from a search."""
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
