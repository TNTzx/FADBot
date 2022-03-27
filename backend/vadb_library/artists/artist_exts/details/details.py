"""Details."""


from ... import artist_struct
from . import aliases as al
from . import image_info as i_i
from . import music_info as m_i
from . import socials as so


class Details(artist_struct.ArtistStruct):
    """Artist details."""
    def __init__(
            self,
            description: str | None = None,
            notes: str | None = None,
            aliases: al.Aliases = al.Aliases(),
            image_info: i_i.ImageInfo = i_i.ImageInfo(),
            music_info: m_i.MusicInfo = m_i.MusicInfo(),
            socials: so.Socials = so.Socials()
            ):
        self.description = description
        self.notes = notes
        self.aliases = aliases
        self.image_info = image_info
        self.music_info = music_info
        self.socials = socials


    def firebase_to_json(self):
        return {
            "description": self.description,
            "notes": self.notes,
            "aliases": self.aliases.firebase_to_json(),
            "image_info": self.image_info.firebase_to_json()
        }
