"""Details."""


from ... import artist_struct as a_s


class Details(a_s.ArtistStruct):
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