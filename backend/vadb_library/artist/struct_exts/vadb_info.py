"""Stores VADB-related info."""


import backend.utils.new_dataclass as dt

from .. import artist_struct as a_s


class VADBInfo(dt.Dataclass):
    """VADB info of the artist."""
    def __init__(
            self,
            artist_id: int = 0
            ):
        self.artist_id = artist_id

    def get_page_link(self):
        """Gets the page of the artist."""
        return f"https://fadb.live/artist/{self.artist_id}"