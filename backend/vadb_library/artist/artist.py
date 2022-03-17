"""Contains logic for storing artists."""


from __future__ import annotations

import typing as typ
import requests as req

import backend.other_functions as o_f

from .. import api

from . import struct_exts as exts
from . import exceptions as a_exc
from . import artist_struct as a_s


def none_if_empty(obj: typ.Iterable):
    """Returns None if the iterable and the iterables inside it is empty or has only None, else return the iterable."""
    def check_if_not_empty(obj: typ.Iterable):
        """Returns False if this iterable is empty, If it's not an iterable, return True."""
        try:
            len(obj)
        except TypeError:
            return True

        if isinstance(obj, str):
            if len(obj) > 0:
                return True

        for item in obj:
            if check_if_not_empty(item):
                return True

        return False

    if check_if_not_empty(obj):
        return obj
    
    return None


class Artist(a_s.ArtistStruct):
    """An artist."""
    def __init__(
            self,
            name: str | None = None,
            proof: str = exts.DEFAULT_PROOF,
            vadb_info: exts.VADBInfo = exts.VADBInfo(),
            states: exts.States = exts.States(),
            details: exts.Details = exts.Details()
            ):
        self.name = name
        self.proof = proof
        self.vadb_info = vadb_info
        self.states = states
        self.details = details


    def send_create(self):
        """Creates the artist in VADB and replaces this `Artist`'s ID with the response from VADB."""
        payload = {
            "name": self.name,
            "status": self.states.status.value,
            "availability": self.states.availability.value
        }
        response = api.make_request(api.Endpoints.artist_create(), payload = payload)

        response_json = response.json()
        response_data = response_json["data"]
        self.vadb_info.artist_id = response_data["id"]

        return response


    def send_edit(self, artist_id: int = None):
        """Edits the artist in VADB with this object's artist ID unless specified."""
        if artist_id is None:
            artist_id = self.vadb_info.artist_id

        payload = {
            "name": self.name,
            "aliases": none_if_empty([
                {
                    "name": alias.name
                } for alias in self.details.aliases.aliases
            ]),
            "status": self.states.status.value,
            "availability": self.states.availability.value,
            "description": self.details.description,
            "notes": self.details.notes,
            "tracks": self.details.music_info.track_count,
            "genre": self.details.music_info.genre,
            "usageRights": none_if_empty([
                {
                    "name": usage_right.description,
                    "value": usage_right.is_verified
                } for usage_right in self.states.usage_rights.usage_rights
            ]),
            "socials": none_if_empty([
                {
                    "link": social.link,
                    "type": social.get_domain()
                } for social in self.details.socials.socials
            ]),
        }
        files = self.details.image_info.to_payload()

        response = api.make_request(api.Endpoints.artist_update(artist_id), payload = payload, files = files)

        return response



    @classmethod
    def from_vadb_receive(cls, response: req.models.Response):
        try:
            response.raise_for_status()
        except req.HTTPError as exc:
            raise a_exc.VADBError("Response not okay.") from exc

        data = response.json()["data"]

        artist_id = data["id"]

        try:
            return cls(
                name = none_if_empty(data["name"]),
                proof = None, # please nao have a proof field :(
                vadb_info = exts.VADBInfo(
                    artist_id = artist_id
                ),
                states = exts.States(
                    status = data["status"],
                    availability = data["availability"],
                    usage_rights = exts.UsageRights(
                        usage_rights = none_if_empty([
                            exts.UsageRight(
                                description = usage_right["name"],
                                is_verified = usage_right["value"]
                            ) for usage_right in data["usageRights"]
                        ])
                    )
                ),
                details = exts.Details(
                    description = none_if_empty(data["description"]),
                    notes = none_if_empty(data["notes"]),
                    aliases = exts.Aliases(
                        aliases = none_if_empty([
                            exts.Alias(
                                name = alias["name"]
                            ) for alias in data["aliases"]
                        ])
                    ),
                    image_info = exts.ImageInfo(
                        avatar = exts.Avatar.from_artist(artist_id),
                        banner = exts.Banner.from_artist(artist_id)
                    ),
                    music_info = exts.MusicInfo(
                        track_count = data["tracks"],
                        genre = none_if_empty(data["genre"])
                    ),
                    socials = exts.Socials(
                        socials = none_if_empty([
                            exts.Social(
                                link = social["link"]
                            ) for social in data["details"]["socials"]
                        ])
                    )
                )
            )
        except Exception as exc:
            raise a_exc.VADBInvalidResponse(f"Invalid response: {o_f.pr_print(data)}.") from exc


    @classmethod
    def from_artist_id(cls, artist_id: int):
        """Returns the `Artist` from an ID from VADB."""
        try:
            return cls.from_vadb_receive(api.make_request(api.Endpoints.artist_get(artist_id)))
        except req.HTTPError as exc:
            raise a_exc.VADBNoArtistID(artist_id) from exc
