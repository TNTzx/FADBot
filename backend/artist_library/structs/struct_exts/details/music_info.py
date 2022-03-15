"""Music info."""


from ... import artist_struct as a_s


class MusicInfo(a_s.ArtistStruct):
    """Stores the information about the artist's music."""
    def __init__(
            self,
            track_count: int = 0,
            genre: str | None = None
            ):
        self.track_count = track_count
        self.genre = genre
