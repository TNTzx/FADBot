"""A VADB-friendly API using the main `Artist` class."""


import requests as req

import backend.databases.api.vadb_interact as v_i
import backend.utils.new_dataclass as dt

from . import artist
from . import artist_struct


class VADBArtist(artist_struct.ArtistStruct, dt.SubDataclass, dt.APIDataclass):
    """Parent class of VADB artists."""


class HasBasicInfo(VADBArtist):
    """Inherited to for basic info."""
    def __init__(
            self,
            name: str | None = None,
            status: int = 2,
            availability: int = 2
            ):
        super().__init__()
        self.name = name
        self.status = status
        self.availability = availability


class VADBCreate(HasBasicInfo):
    """Creates a framework for creating an artist in VADB."""
    def send_data(self):
        return v_i.make_request("POST", "/artist/", self.get_json_dict())

    @classmethod
    def from_main(cls, data: artist.Artist):
        return cls(
            name = data.name,
            status = data.states.status.value,
            availability = data.states.availability.value
        )


class VADBEdit(HasBasicInfo):
    """Creates a framework for editing an artist in VADB."""
    def __init__(
            self,
            artist_id: int = 0,
            name: str | None = None,
            status: int | None = 2,
            availability: int | None = 2,
            usage_rights: list[artist.UsageRight] | None = None,
            aliases: list[artist.Alias] | None = None,
            description: str | None = None,
            notes: str | None = None,
            track_count: int | None = 0,
            genre: str | None = None,
            avatar_url: str = artist.DEFAULT_IMAGE,
            banner_url: str = artist.DEFAULT_IMAGE,
            socials: list[artist.Social] = None
            ):
        super().__init__(name, status, availability)
        self.artist_id = artist_id
        self.usage_rights = usage_rights
        self.aliases = aliases
        self.description = description
        self.notes = notes
        self.track_count = track_count
        self.genre = genre
        self.avatar_url = avatar_url
        self.banner_url = banner_url
        self.socials = socials


    def send_data(self):
        return v_i.make_request("POST", f"/artist/{self.artist_id}", self.get_json_dict())


    def to_dict(self):
        return {
            "name": self.name,

            "status": self.status,
            "availability": self.availability,
            "usageRights": self.usage_rights,

            "aliases": [{"name": alias.name} for alias in self.aliases],
            "description": self.description,
            "notes": self.notes,
            "tracks": self.track_count,
            "genre": self.genre,
            "avatarUrl": self.avatar_url,
            "bannerUrl": self.banner_url,
            "socials": self.socials
        }

    @classmethod
    def from_main(cls, data: artist.Artist):
        return cls(
            artist_id = data.vadb_info.artist_id,
            name = data.name,
            status = data.states.status.value,
            availability = data.states.availability.value,
            usage_rights = data.states.usage_rights,
            aliases = data.details.aliases,
            description = data.details.description,
            notes = data.details.notes,
            track_count = data.details.music_info.track_count,
            genre = data.details.music_info.genre,
            avatar_url = data.details.image_info.avatar_url,
            banner_url = data.details.image_info.banner_url,
            socials = data.details.socials
        )


class VADBDelete(VADBArtist):
    """Contains a framework for completely obliterating an artist."""
    def __init__(self, artist_id: int = 0):
        self.artist_id = artist_id
    
    def send_data(self):
        return v_i.make_request("DELETE", f"/artist/{self.artist_id}")


    @classmethod
    def from_main(cls, data: artist.Artist) -> None:
        return cls(artist_id = data.vadb_info.artist_id)


class VADBReceive(HasBasicInfo):
    """Contains a framework for received artists from VADB."""
    def __init__(
            self,
            artist_id: int = 0,
            name: str | None = None,
            status: int | None = 2,
            availability: int | None = 2,
            usage_rights: list[artist.UsageRight] | None = None,
            aliases: list[artist.Alias] | None = None,
            description: str | None = None,
            notes: str | None = None,
            track_count: int | None = 0,
            genre: str | None = None,
            avatar_url: str = artist.DEFAULT_IMAGE,
            banner_url: str = artist.DEFAULT_IMAGE,
            socials: list[artist.Social] = None
            ):
        super().__init__(name = name, status = status, availability = availability)
        self.artist_id = artist_id
        self.usage_rights = usage_rights
        self.aliases = aliases
        self.description = description
        self.notes = notes
        self.track_count = track_count
        self.genre = genre
        self.details = self.Details(avatar_url = avatar_url, banner_url = banner_url, socials = socials)

    class Details(dt.APIDataclass):
        """Contains details."""
        def __init__(
                self,
                avatar_url: str = artist.DEFAULT_IMAGE,
                banner_url: str = artist.DEFAULT_IMAGE,
                socials: list[artist.Social] = None
                ):
            self.avatar_url = avatar_url
            self.banner_url = banner_url
            self.socials = socials

        @classmethod
        def from_dict_response(cls, response: dict):
            pass

    @classmethod
    def from_dict_response(cls, response: dict):
        
        return super().from_obj_response(response)


    @classmethod
    def get_from_id(cls, artist_id: int):
        """Returns the result of an ID search."""
        response = v_i.make_request("GET", f"/artist/{artist_id}")
        
