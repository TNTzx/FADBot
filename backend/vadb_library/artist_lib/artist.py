"""Contains logic for storing artists."""


from __future__ import annotations

import re

import requests as req
import backend.other as ot

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
            proof: artist_exts.Proof = artist_exts.Proof(),
            vadb_info: artist_exts.VADBInfo = artist_exts.VADBInfo(),
            states: artist_exts.States = artist_exts.States(),
            details: artist_exts.Details = artist_exts.Details()
            ):
        self.name = name
        self.proof = proof
        self.vadb_info = vadb_info
        self.states = states
        self.details = details


    def __eq__(self, other: Artist):
        return self.firebase_to_json() == other.firebase_to_json()


    def vadb_to_create_json(self) -> dict | list:
        return {
            "name": self.name,
            "status": self.states.status.value,
            "availability": self.states.availability.value
        }

    def vadb_create(self):
        """Creates the artist in VADB and replaces this `Artist`'s ID with the response from VADB.

        Send:
        ```
        {
            "name": str,
            "status": int,
            "availability": int
        }
        ```

        Receive:
        ```
        {
            "code": 200,
            "data": {
                "id": int
            }
        }
        ```
        """
        payload = self.vadb_to_create_json()

        try:
            response = api.make_request(api.Endpoints.artist_create(), payload = payload)
        except req.HTTPError as exc:
            if api.excs.check_artist_already_exists(exc.response):
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
            "usageRights": self.states.usage_rights.vadb_to_edit_json(),
            "socials": self.details.socials.vadb_to_edit_json(),
        }

    def vadb_edit(self, artist_id: int = None):
        """Edits the artist in VADB with this object's artist ID unless specified.

        Send:
        ```
        {
            "name": str,
            "aliases": [
                {
                    "name": str
                }, ...
            ],
            "status": int,
            "availability": int,
            "description": str,
            "notes": str,
            "avatar": ("file"),
            "banner": ("file"),
            "tracks": int,
            "genre": str,
            "usageRights": [
                {
                    "name": str,
                    "value": bool
                }, ...
            ],
            "socials": [
                {
                    "link": str,
                    "type": str
                }, ...
            ],
        }
        ```
        Receive:
        ```
        {
            "code": 200,
            "data": {
                "changed": [
                    ...
                ]
            }
        }
        ```"""
        if artist_id is None:
            artist_id = self.vadb_info.artist_id

        payload = self.vadb_to_edit_json()
        files = self.details.image_info.to_payload()

        try:
            response = api.make_request(api.Endpoints.artist_update(artist_id), payload = payload, files = files)
        except req.HTTPError as exc:
            if api.excs.check_artist_already_exists(exc.response):
                raise excepts.VADBAlreadyExistingArtist(self.name) from exc

            raise excepts.VADBInvalidResponse from exc


        return response


    def vadb_create_edit(self):
        """Creates and edits the artist to make an entry in VADB."""
        self.vadb_create()
        self.vadb_edit()


    @classmethod
    def vadb_from_get_json(cls, json: dict | list):
        """Returns an `Artist` from a VADB data structure.
        Receive:
        ```
        "data": {
            'id': int,
            'name': str,
            'aliases': [
                {
                    'name': str
                }, ...
            ],
            'description': str,
            'tracks': int,
            'genre': str,
            'status': int,
            'availability': int,
            'notes': str,
            'usageRights': [
                {
                    'name': str,
                    'value': bool
                },
                {
                    'name': str,
                    'value': bool
                }
            ],
            'details': {
                'socials': [
                    {
                        'link': str,
                        'type': str
                    }, ...
                ]
            }
        }
        ```
        """
        artist_id = json["id"]

        try:
            return cls(
                name = clean_iter.clean_iterable(json["name"]),
                # proof = please nao have a proof field :(,
                vadb_info = artist_exts.VADBInfo(
                    artist_id = artist_id
                ),
                states = artist_exts.States(
                    status = json["status"],
                    availability = json["availability"],
                    usage_rights = artist_exts.UsageRights(
                        usage_rights = clean_iter.clean_iterable([
                            artist_exts.UsageRight(
                                description = usage_right["name"],
                                is_verified = usage_right["value"]
                            ) for usage_right in json["usageRights"]
                        ])
                    )
                ),
                details = artist_exts.Details(
                    description = clean_iter.clean_iterable(json["description"]),
                    notes = clean_iter.clean_iterable(json["notes"]),
                    aliases = artist_exts.Aliases(
                        aliases = clean_iter.clean_iterable([
                            artist_exts.Alias(
                                name = alias["name"]
                            ) for alias in json["aliases"]
                        ])
                    ),
                    image_info = artist_exts.ImageInfo(
                        avatar = artist_exts.Avatar.from_artist(artist_id),
                        banner = artist_exts.Banner.from_artist(artist_id)
                    ),
                    music_info = artist_exts.MusicInfo(
                        track_count = json["tracks"],
                        genre = clean_iter.clean_iterable(json["genre"])
                    ),
                    socials = artist_exts.Socials(
                        socials = clean_iter.clean_iterable([
                            artist_exts.Social(
                                link = social["link"]
                            ) for social in json["details"]["socials"]
                        ])
                    )
                )
            )
        except Exception as exc:
            raise excepts.VADBInvalidResponse(f"Invalid response: {ot.pr_print(json)}.") from exc

    @classmethod
    def vadb_from_id(cls, artist_id: int):
        """Returns the `Artist` from an ID from VADB."""
        try:
            return cls.vadb_from_get_json(
                api.make_request(api.Endpoints.artist_get(artist_id)).json()["data"]
            )
        except req.HTTPError as exc:
            raise excepts.VADBNoArtistID(artist_id) from exc


    def firebase_to_json(self):
        return {
            "name": self.name,
            "proof": self.proof.firebase_to_json(),
            "vadb_info": self.vadb_info.firebase_to_json(),
            "states": self.states.firebase_to_json(),
            "details": self.details.firebase_to_json()
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        return cls(
            name = json.get("name"),
            proof = artist_exts.Proof.firebase_from_json(json.get("proof")),
            vadb_info = artist_exts.VADBInfo.firebase_from_json(json.get("vadb_info")),
            states = artist_exts.States.firebase_from_json(json.get("states")),
            details = artist_exts.Details.firebase_from_json(json.get("details"))
        )


    def check_if_match_query(self, search_term: str):
        """Returns `True` if this `Artist` matches the search term. Returns `False` otherwise."""
        pattern = re.compile(".*".join(search_term), flags = re.IGNORECASE)

        aliases = self.details.aliases.aliases if self.details.aliases.aliases is not None else []
        full_name_list = [self.name] + [alias.name for alias in aliases]

        for item in full_name_list:
            if bool(pattern.search(item)):
                return True

        return False
