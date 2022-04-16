"""Artist query object."""


import nextcord as nx

import requests as req

from .. import queries
from .. import excepts
from .. import api
from . import artist


class ArtistQuery(queries.BaseQuery):
    """Artist query."""
    def __init__(self, query_items: list[artist.Artist] = None):
        self.query_items = query_items


    @classmethod
    def from_search(cls, search_term: str):
        """Creates an `ArtistQuery` from a search term."""
        try:
            response = api.make_request(api.Endpoints.artist_search(search_term)).json()
        except req.exceptions.HTTPError as exc:
            raise excepts.VADBNoSearchResult(search_term) from exc

        return cls(
            query_items = [
                artist.Artist.vadb_from_get_json(artist_data)
                for artist_data in response["data"]
            ]
        )


    def generate_embed(
            self,
            title: str = None,
            description: str = None,
            footer: str = None
            ):
        """Generates an embed for multiple artists."""
        embed = nx.Embed(
            color = 0xFF0000,
            title = title,
            description = description
        )

        emb_artists = [
            f"**{artist.vadb_info.artist_id}**: {artist.name}"
            for artist in self.query_items
        ]
        embed.add_field(
            name = "_ _",
            value = "\n".join(emb_artists)
        )

        if footer is not None:
            embed.set_footer(text = footer)

        return embed
