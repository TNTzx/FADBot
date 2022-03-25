"""Contains logic for storing artists."""


from __future__ import annotations

import requests as req

import backend.other_functions as o_f

from .. import api
from ..other import clean_iter

from .. import excepts
from . import artist_exts
from . import artist_struct


class Artist(artist_struct.ArtistStruct):
    """An artist."""
    def __init__(
            self,
            name: str | None = None,
            proof: artist_exts.Proof = artist_exts.DEFAULT_PROOF,
            vadb_info: artist_exts.VADBInfo = artist_exts.VADBInfo(),
            states: artist_exts.States = artist_exts.States(),
            details: artist_exts.Details = artist_exts.Details()
            ):
        self.name = name
        self.proof = proof
        self.vadb_info = vadb_info
        self.states = states
        self.details = details


    def vadb_to_create_json(self) -> dict | list:
        super().vadb_to_create_json()
        return {
            "name": self.name,
            "status": self.states.status.value,
            "availability": self.states.availability.value
        }

    def vadb_create(self):
        """Creates the artist in VADB and replaces this `Artist`'s ID with the response from VADB."""
        payload = self.vadb_to_create_json()

        try:
            response = api.make_request(api.Endpoints.artist_create(), payload = payload)
        except req.HTTPError as exc:
            if api.exc.check_artist_already_exists(exc.response):
                raise excepts.VADBAlreadyExistingArtist(self.name) from exc

            raise excepts.VADBInvalidResponse()

        response_json = response.json()
        response_data = response_json["data"]
        self.vadb_info.artist_id = response_data["id"]

        return response


    def vadb_to_edit_json(self) -> dict | list:
        return {
            "name": self.name,
            "aliases": self.details.aliases.vadb_to_edit_json(),
            "status": self.states.status.value,
            "availability": self.states.availability.value,
            "description": self.details.description,
            "notes": self.details.notes,
            "tracks": self.details.music_info.track_count,
            "genre": self.details.music_info.genre,
            "usageRights": (
                clean_iter.clean_iterable([
                    {
                        "name": usage_right.description,
                        "value": usage_right.is_verified
                    } for usage_right in self.states.usage_rights.usage_rights
                ]) if self.states.usage_rights.usage_rights is not None else None
            ),
            "socials": (
                clean_iter.clean_iterable([
                    {
                        "link": social.link,
                        "type": social.get_domain()
                    } for social in self.details.socials.socials
                ]) if self.details.socials.socials is not None else None
            ),
        }

    def vadb_edit(self, artist_id: int = None):
        """Edits the artist in VADB with this object's artist ID unless specified."""
        if artist_id is None:
            artist_id = self.vadb_info.artist_id

        payload = {
            "name": self.name,
            "aliases": (
                clean_iter.clean_iterable([
                    {
                        "name": alias.name
                    } for alias in self.details.aliases.aliases
                ]) if self.details.aliases.aliases is not None else None
            ),
            "status": self.states.status.value,
            "availability": self.states.availability.value,
            "description": self.details.description,
            "notes": self.details.notes,
            "tracks": self.details.music_info.track_count,
            "genre": self.details.music_info.genre,
            "usageRights": (
                clean_iter.clean_iterable([
                    {
                        "name": usage_right.description,
                        "value": usage_right.is_verified
                    } for usage_right in self.states.usage_rights.usage_rights
                ]) if self.states.usage_rights.usage_rights is not None else None
            ),
            "socials": (
                clean_iter.clean_iterable([
                    {
                        "link": social.link,
                        "type": social.get_domain()
                    } for social in self.details.socials.socials
                ]) if self.details.socials.socials is not None else None
            ),
        }
        files = self.details.image_info.to_payload()

        try:
            response = api.make_request(api.Endpoints.artist_update(artist_id), payload = payload, files = files)
        except req.HTTPError as exc:
            if api.exc.check_artist_already_exists(exc.response):
                raise excepts.VADBAlreadyExistingArtist(self.name) from exc

            raise excepts.VADBInvalidResponse from exc


        return response



    @classmethod
    def vadb_from_json(cls, data: dict):
        """Returns an `Artist` from a VADB data structure."""
        artist_id = data["id"]

        try:
            return cls(
                name = clean_iter.clean_iterable(data["name"]),
                proof = None, # please nao have a proof field :(
                vadb_info = artist_exts.VADBInfo(
                    artist_id = artist_id
                ),
                states = artist_exts.States(
                    status = data["status"],
                    availability = data["availability"],
                    usage_rights = artist_exts.UsageRights(
                        usage_rights = clean_iter.clean_iterable([
                            artist_exts.UsageRight(
                                description = usage_right["name"],
                                is_verified = usage_right["value"]
                            ) for usage_right in data["usageRights"]
                        ])
                    )
                ),
                details = artist_exts.Details(
                    description = clean_iter.clean_iterable(data["description"]),
                    notes = clean_iter.clean_iterable(data["notes"]),
                    aliases = artist_exts.Aliases(
                        aliases = clean_iter.clean_iterable([
                            artist_exts.Alias(
                                name = alias["name"]
                            ) for alias in data["aliases"]
                        ])
                    ),
                    image_info = artist_exts.ImageInfo(
                        avatar = artist_exts.Avatar.from_artist(artist_id),
                        banner = artist_exts.Banner.from_artist(artist_id)
                    ),
                    music_info = artist_exts.MusicInfo(
                        track_count = data["tracks"],
                        genre = clean_iter.clean_iterable(data["genre"])
                    ),
                    socials = artist_exts.Socials(
                        socials = clean_iter.clean_iterable([
                            artist_exts.Social(
                                link = social["link"]
                            ) for social in data["details"]["socials"]
                        ])
                    )
                )
            )
        except Exception as exc:
            raise excepts.VADBInvalidResponse(f"Invalid response: {o_f.pr_print(data)}.") from exc


    @classmethod
    def vadb_from_id(cls, artist_id: int):
        """Returns the `Artist` from an ID from VADB."""
        try:
            return cls.vadb_from_json(api.make_request(api.Endpoints.artist_get(artist_id)).json()["data"])
        except req.HTTPError as exc:
            raise excepts.VADBNoArtistID(artist_id) from exc
