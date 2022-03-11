"""Contains logic for storing artists."""


from __future__ import annotations

import tldextract as tld

import backend.utils.new_dataclass as dt
import backend.utils.other as other

from . import states as st


DEFAULT_IMAGE = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"


class ArtistDefault(dt.Dataclass):
    """An artist."""
    def __init__(
            self,
            name = "<default name>",
            proof = DEFAULT_IMAGE,
            vadb_info: VADBInfo = None,
            states: States = None
            ):
        self.name = name
        self.proof = proof

        if vadb_info is None:
            vadb_info = VADBInfo()
        self.vadb_info = vadb_info

        if states is None:
            states = States()
        self.vadb_info = states


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


class States(dt.Dataclass):
    """States."""
    def __init__(
            self,
            status: int = 2,
            availability: int = 2
            ):
        self.status = other.Match(st.StateList.get_states_dict(), status)
        self.availability = other.Match(st.AvailabilityList.get_states_dict(), availability)


class Details(dt.DataclassSub):
    """Artist details."""
    def __init__(
            self,
            description: str = "No description.",
            notes: str = "No notes.",
            aliases: list[Alias] = None,
            image_info: ImageInfo = None,
            music_info: MusicInfo = None,
            socials: list[Social] = None
            ):
        self.description = description
        self.notes = notes
        self.aliases = aliases
        self.images = image_info
        self.music_info = music_info
        self.socials = socials

class Alias(dt.Dataclass):
    """Stores an alias."""
    def __init__(self) -> None:
        self.name = None

class ImageInfo(dt.Dataclass):
    """Stores the images of the artist."""
    def __init__(self):
        self.avatar_url = DEFAULT_IMAGE
        self.banner_url = DEFAULT_IMAGE

class MusicInfo(dt.Dataclass):
    """Stores the information about the artist's music."""
    def __init__(self):
        self.tracks = 0
        self.genre = None

class Social(dt.Dataclass):
    """Defines a social."""
    def __init__(self, link: str = "https://fadb.live"):
        self.link = link

    def get_domain(self):
        """Gets the domain of the social link."""
        return tld.extract(self.link).domain
