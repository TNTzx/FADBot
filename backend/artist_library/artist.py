"""Contains logic for storing artists."""


from __future__ import annotations

import backend.utils.new_dataclass as dt
import backend.utils.other as other

from . import states


DEFAULT_IMAGE = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"


class ArtistDefault(dt.Dataclass):
    """An artist."""
    def __init__(
            self,
            name = "<default name>",
            proof = DEFAULT_IMAGE,
            vadb_info: ArtistDefault.VADBInfo = None,
            states: ArtistDefault.States = None
            ):
        self.name = name
        self.proof = proof

        if vadb_info == None:
            vadb_info = self.VADBInfo()
        self.vadb_info = vadb_info

        if states == None:
            states = self.States()
        self.vadb_info = states


    class VADBInfo(dt.Dataclass):
        """VADB info."""
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
            self.status = other.Match(states.StateList.get_states_dict(), status)
            self.availability = other.Match(states.AvailabilityList.get_states_dict(), availability)
