"""Contains logic for storing artists."""


from __future__ import annotations

import typing as typ
import requests as req

import backend.databases.vadb.vadb_interact as v_i

from . import exceptions as a_exc
from . import artist_struct as a_s

from .struct_exts.details import image_info as i_i
from .struct_exts import vadb_info as v_inf
from .struct_exts.states import states as st
from .struct_exts.states import usage_rights as u_r
from .struct_exts.details import details as det
from .struct_exts.details import aliases as al
from .struct_exts.details import music_info as m_i
from .struct_exts.details import socials as so

import backend.other_functions as o_f


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
            proof: str = i_i.DEFAULT_IMAGE,
            vadb_info: v_inf.VADBInfo = v_inf.VADBInfo(),
            states: st.States = st.States(),
            details: det.Details = det.Details()
            ):
        self.name = name
        self.proof = proof
        self.vadb_info = vadb_info
        self.states = states
        self.details = details


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
                vadb_info = v_inf.VADBInfo(
                    artist_id = artist_id
                ),
                states = st.States(
                    status = data["status"],
                    availability = data["availability"],
                    usage_rights = u_r.UsageRights(
                        usage_rights = none_if_empty([
                            u_r.UsageRight(
                                description = usage_right["name"],
                                is_verified = usage_right["value"]
                            ) for usage_right in data["usageRights"]
                        ])
                    )
                ),
                details = det.Details(
                    description = none_if_empty(data["description"]),
                    notes = none_if_empty(data["notes"]),
                    aliases = al.Aliases(
                        aliases = none_if_empty([
                            al.Alias(
                                name = alias["name"]
                            ) for alias in data["aliases"]
                        ])
                    ),
                    image_info = i_i.ImageInfo(
                        avatar = i_i.Image.from_artist(artist_id, i_i.ImageTypes.avatar),
                        banner = i_i.Image.from_artist(artist_id, i_i.ImageTypes.banner)
                    ),
                    music_info = m_i.MusicInfo(
                        track_count = data["tracks"],
                        genre = none_if_empty(data["genre"])
                    ),
                    socials = so.Socials(
                        socials = none_if_empty([
                            so.Social(
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
            return cls.from_vadb_receive(v_i.make_request("GET", f"/artist/{artist_id}"))
        except req.HTTPError as exc:
            raise a_exc.VADBNoArtistID(artist_id) from exc
