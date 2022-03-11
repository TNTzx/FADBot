"""A VADB-friendly API using the main `Artist` class."""


import backend.utils.new_dataclass as dt

import backend.databases.vadb.vadb_interact as v_i

from .. import artist


class VADBArtist(dt.SubDataclass):
    """Parent class of VADB artists."""
    def __init__(
            self,
            name: str = "<default name>",
            status: int = 2,
            availability: int = 2
            ):
        self.name = name
        self.status = status
        self.availability = availability


class VADBCreate(VADBArtist):
    """Creates a framework for creating an artist in VADB."""
    def send_data(self):
        """Creates the artist using the current instance."""
        return v_i.make_request("POST", "/artist/", self.to_dict())


    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "availability": self.availability
        }

    @classmethod
    def from_main(cls, data: artist.Artist):
        return cls(
            name = data.name,
            status = data.states.status.value,
            availability = data.states.availability.value
        )


class VADBEdit(VADBArtist):
    """Creates a framework for editing an artist in VADB."""
    def __init__(
            self,
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
        self.usage_rights = usage_rights
        self.aliases = aliases
        self.description = description
        self.notes = notes
        self.track_count = track_count
        self.genre = genre
        self.avatar_url = avatar_url
        self.banner_url = banner_url
        self.socials = socials


    def to_dict(self):
        return {
            "name": self.name,

            "status": data.states.status.value,
            "availability": data.states.availability.value,
            "usageRights": data.states.usage_rights,

            "aliases": [{"name": alias.name} for alias in data.details.aliases],
            "description": data.details.description,
            "notes": data.details.notes,
            "tracks": data.details.music_info.tracks,
            "genre": data.details.music_info.genre,
            "avatarUrl": data.details.images.avatar_url,
            "bannerUrl": data.details.images.banner_url,
            "socials": data.details.socials
        }

    @classmethod
    def from_main(cls, data: artist.Artist):
        return cls(
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
