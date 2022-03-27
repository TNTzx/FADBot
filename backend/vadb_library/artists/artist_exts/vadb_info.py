"""Stores VADB-related info."""


from .. import artist_struct


class VADBInfo(artist_struct.ArtistStruct):
    """VADB info of the artist."""
    def __init__(
            self,
            artist_id: int = None
            ):
        self.artist_id = artist_id

    def get_page_link(self):
        """Gets the page of the artist."""
        if self.artist_id is not None:
            return f"https://fadb.live/artist/{self.artist_id}"

        return None


    def firebase_to_json(self):
        return {
            "artist_id": self.artist_id
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list | ...):
        return cls(
            artist_id = json.get("artist_id")
        )
