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


    @classmethod
    def vadb_from_get_json(cls, json: dict | list | int | str) -> None:
        return cls(
            artist_id = json
        )
