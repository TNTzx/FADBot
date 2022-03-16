"""Stores endpoints."""


import urllib.parse as ul

import backend.utils.new_dataclass as dt

from . import consts


class RequestTypes:
    """Stores request types."""
    get = "GET"
    post = "POST"
    patch = "PATCH"
    delete = "DELETE"


class Endpoint(dt.Dataclass):
    """Stores information about an endpoint."""
    def __init__(
                self,
                request_type: str,
                link: str
            ):
        self.request_type = request_type
        self.link = link


def append_to_api_link(append_link: str):
    """Appends a link to the API link."""
    return f"{consts.API_LINK}{append_link}"


def artist_id_link(artist_id: int):
    """Returns a link with the artist id."""
    return append_to_api_link(f"/artist/{artist_id}")


class Endpoints():
    """Stores all endpoints."""
    @classmethod
    def artist_get(cls, artist_id: int):
        """`GET` Endpoint for getting an artist."""
        return Endpoint(RequestTypes.get, artist_id_link(artist_id))

    @classmethod
    def artist_search(cls, search_term: str):
        """`GET` Endpoint for getting a search term."""
        search_term_url = ul.quote_plus(search_term)
        search_term_url = search_term_url.replace("+", "%20")
        Endpoint(RequestTypes.get, append_to_api_link(f"/search/{search_term_url}"))


    @classmethod
    def artist_create(cls):
        """`POST` Endpoint for artist creation."""
        return Endpoint(RequestTypes.post, append_to_api_link("/artist"))

    @classmethod
    def artist_update(cls, artist_id: int):
        """`PATCH` Endpoint for artist updating."""
        return Endpoint(RequestTypes.patch, artist_id_link(artist_id))

    @classmethod
    def artist_delete(cls, artist_id: int):
        """`DELETE` Endpoint for artist deletion."""
        return Endpoint(RequestTypes.delete, artist_id_link(artist_id))


    @classmethod
    def fun(cls):
        """`GET` Wow, how fun! Teapot! :D"""
        return Endpoint(RequestTypes.get, f"{consts.BASE_LINK}/teapot")