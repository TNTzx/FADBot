"""Contains logic for storing artists."""


from __future__ import annotations

import typing as typ
import requests as req

import backend.other_functions as o_f

from .. import api
from ..other import clean_iter

from . import struct_exts as exts
from . import exceptions as a_exc
from . import artist_struct as a_s


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
            "aliases": clean_iter.clean_iterable([
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
            "usageRights": clean_iter.clean_iterable([
                {
                    "name": usage_right.description,
                    "value": usage_right.is_verified
                } for usage_right in self.states.usage_rights.usage_rights
            ]),
            "socials": clean_iter.clean_iterable([
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
                name = clean_iter.clean_iterable(data["name"]),
                proof = None, # please nao have a proof field :(
                vadb_info = exts.VADBInfo(
                    artist_id = artist_id
                ),
                states = exts.States(
                    status = data["status"],
                    availability = data["availability"],
                    usage_rights = exts.UsageRights(
                        usage_rights = clean_iter.clean_iterable([
                            exts.UsageRight(
                                description = usage_right["name"],
                                is_verified = usage_right["value"]
                            ) for usage_right in data["usageRights"]
                        ])
                    )
                ),
                details = exts.Details(
                    description = clean_iter.clean_iterable(data["description"]),
                    notes = clean_iter.clean_iterable(data["notes"]),
                    aliases = exts.Aliases(
                        aliases = clean_iter.clean_iterable([
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
                        genre = clean_iter.clean_iterable(data["genre"])
                    ),
                    socials = exts.Socials(
                        socials = clean_iter.clean_iterable([
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
