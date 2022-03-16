"""Contains logic for storing artists."""


from __future__ import annotations

import typing as typ
import requests as req

import backend.databases.vadb as vadb
import backend.other_functions as o_f

from . import struct_exts as exts
from . import exceptions as a_exc
from . import artist_struct as a_s


def none_if_empty(obj: typ.Iterable):
    """Returns None if the iterable is empty, else return the iterable."""
    if len(obj) == 0:
        return None

    return obj


class Artist(a_s.ArtistStruct):
    """An artist."""
    def __init__(
            self,
            name: str | None = None,
            proof: str = exts.pack_details.mod_image_info.DEFAULT_PROOF,
            vadb_info: exts.VADBInfo = exts.VADBInfo(),
            states: exts.pack_states.States = exts.pack_states.States(),
            details: exts.pack_details.Details = exts.pack_details.Details()
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
        response = vadb.v_i.make_request(vadb.endp.Endpoints.artist_create(), payload = payload, to_dict = True)

        response_data = response["data"]
        self.vadb_info.artist_id = response_data["id"]





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
                states = exts.pack_states.States(
                    status = data["status"],
                    availability = data["availability"],
                    usage_rights = exts.pack_states.UsageRights(
                        usage_rights = none_if_empty([
                            exts.pack_states.UsageRight(
                                description = usage_right["name"],
                                is_verified = usage_right["value"]
                            ) for usage_right in data["usageRights"]
                        ])
                    )
                ),
                details = exts.pack_details.Details(
                    description = none_if_empty(data["description"]),
                    notes = none_if_empty(data["notes"]),
                    aliases = exts.pack_details.Aliases(
                        aliases = none_if_empty([
                            exts.details.Alias(
                                name = alias["name"]
                            ) for alias in data["aliases"]
                        ])
                    ),
                    image_info = exts.pack_details.ImageInfo(
                        avatar = exts.pack_details.Avatar.from_artist(artist_id),
                        banner = exts.pack_details.Banner.from_artist(artist_id)
                    ),
                    music_info = exts.pack_details.MusicInfo(
                        track_count = data["tracks"],
                        genre = none_if_empty(data["genre"])
                    ),
                    socials = exts.pack_details.Socials(
                        socials = none_if_empty([
                            exts.pack_details.Social(
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
            return cls.from_vadb_receive(vadb.v_i.make_request(vadb.endp.Endpoints.artist_get(artist_id)))
        except req.HTTPError as exc:
            raise a_exc.VADBNoArtistID(artist_id) from exc
