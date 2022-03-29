"""Contains logic for requests."""


from .. import artists as art
from . import req_struct
from . import req_exts


class ChangeRequest(req_struct.ChangeRequestStructure):
    """Parent class for all requests."""
    def __init__(
            self,
            artist: art.Artist,
            log_bundle: req_exts.LogBundle = req_exts.LogBundle()
            ):
        self.artist = artist
        self.log_bundle = log_bundle


    def firebase_to_json(self):
        return {
            "artist": self.artist.firebase_to_json(),
            "log_bundle": self.log_bundle.firebase_to_json()
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        return cls(
            artist = art.Artist.firebase_from_json(json.get("artist")),
            log_bundle = req_exts.LogBundle.firebase_from_json(json.get("log_bundle"))
        )


    def send_request_discord(self):
        """Sends the request over to Discord."""
        


    # TODO also these methods
    def send_request(self):
        """Sends the request for approval."""
        

    def approve_request(self):
        """Approves the request."""


class AddRequest(ChangeRequest):
    """Request for adding artists into the database."""


class EditRequest(ChangeRequest):
    """Request for editing an artist in the database."""
