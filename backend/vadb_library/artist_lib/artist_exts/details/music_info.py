"""Music info."""


from ... import artist_struct


class MusicInfo(artist_struct.ArtistStruct):
    """Stores the information about the artist's music."""
    def __init__(
            self,
            track_count: int = 0,
            genre: str | None = None
            ):
        self.track_count = track_count
        self.genre = genre


    def firebase_to_json(self):
        return {
            "track_count": self.track_count,
            "genre": self.genre
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        return cls(
            track_count = json.get("track_count"),
            genre = json.get("genre")
        )
