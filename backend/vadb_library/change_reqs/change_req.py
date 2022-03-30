"""Contains logic for requests."""


import backend.firebase as firebase

from .. import artists as art
from . import req_struct
from . import req_exts


class ChangeRequest(req_struct.ChangeRequestStructure):
    """Parent class for all requests."""
    type_: str = None
    firebase_name: str = None

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


    async def discord_send_request_pending(self):
        """The discord part of sending the request for approval."""
        self.log_bundle = await req_exts.LogBundle.send_request_pending_logs(self.artist, self.type_)

    async def firebase_send_request_pending(self):
        """The Firebase part of sending the request for approval."""
        firebase.

    async def send_request_pending(self):
        """Sends the request for approval."""


    def approve_request(self):
        """Approves the request."""


class AddRequest(ChangeRequest):
    """Request for adding artists into the database."""


class EditRequest(ChangeRequest):
    """Request for editing an artist in the database."""
