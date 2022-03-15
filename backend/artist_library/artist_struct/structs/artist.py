"""Contains logic for storing artists."""


from __future__ import annotations

import tldextract as tld

import backend.utils.new_dataclass as dt
import backend.utils.other as util_other

from . import vadb
from .struct_exts import states as st
from .struct_exts import image_info as img



class MusicInfo(dt.Dataclass):
    """Stores the information about the artist's music."""
    def __init__(
            self,
            track_count: int = 0,
            genre: str | None = None
            ):
        self.track_count = track_count
        self.genre = genre

class Social(dt.Dataclass):
    """Defines a social."""
    def __init__(
            self,
            link: str = "https://fadb.live"
        ):
        self.link = link

    def get_domain(self):
        """Gets the domain of the social link."""
        return tld.extract(self.link).domain

class Details(dt.Dataclass):
    """Artist details."""
    def __init__(
            self,
            description: str | None = None,
            notes: str | None = None,
            aliases: list[Alias] | None = None,
            image_info: ImageInfo = ImageInfo(),
            music_info: MusicInfo = MusicInfo(),
            socials: list[Social] | None = None
            ):
        self.description = description
        self.notes = notes

        if aliases is None:
            aliases = []
        self.aliases = aliases
        self.image_info = image_info
        self.music_info = music_info

        if socials is None:
            aliases = []
        self.socials = socials


class Artist(dt.MainDataclass):
    """An artist."""
    def __init__(
            self,
            name: str | None = None,
            proof: str = DEFAULT_IMAGE,
            vadb_info: VADBInfo = VADBInfo(),
            states: States = States(),
            details: Details = Details()
            ):
        self.name = name
        self.proof = proof
        self.vadb_info = vadb_info
        self.states = states
        self.details = details


    def vadb_create(self):
        """Creates the artist on VADB."""

    @classmethod
    def from_sub(
            cls,
            data: dt.SubDataclass
            ) -> None:
        pass
