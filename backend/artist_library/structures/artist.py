"""Contains logic for storing artists."""


from __future__ import annotations

import tldextract as tld

import backend.utils.new_dataclass as dt
import backend.utils.other as other

from .. import states as st


DEFAULT_IMAGE = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"


class VADBInfo(dt.Dataclass):
    """VADB info of the artist."""
    def __init__(
            self,
            artist_id: int = 0
            ):
        self.artist_id = artist_id

    def get_page(self):
        """Gets the page of the artist."""
        return f"https://fadb.live/artist/{self.artist_id}"



class UsageRight(dt.Dataclass):
    """Defines a usage right."""
    def __init__(self,
        description: str | None = None,
        is_verified: bool = True
        ):
        self.description = description
        self.is_verified = is_verified


class States(dt.Dataclass):
    """States."""
    def __init__(
            self,
            status: int = 2,
            availability: int = 2,
            usage_rights: list[UsageRight] | None = None
            ):
        self.status = other.Match(st.StateList.get_states_dict(), status)
        self.availability = other.Match(st.AvailabilityList.get_states_dict(), availability)

        if usage_rights is None:
            usage_rights = []
        self.usage_rights = usage_rights


class Alias(dt.Dataclass):
    """Stores an alias."""
    def __init__(self, name: str | None = None) -> None:
        self.name = name

class ImageInfo(dt.Dataclass):
    """Stores the images of the artist."""
    def __init__(
            self,
            avatar_url: str = DEFAULT_IMAGE,
            banner_url = DEFAULT_IMAGE
            ):
        self.avatar_url = avatar_url
        self.banner_url = banner_url

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


class Artist(dt.Dataclass):
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
