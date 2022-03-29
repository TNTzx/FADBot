"""Contains logic for requests."""


import backend.firebase as firebase

from .. import artists as art
from . import change_req_struct
from . import req_exts


class ChangeRequest(firebase.FBStruct):
    """Parent class for all requests."""
    def __init__(
            self,
            artist: art.Artist,
            log_bundle: req_exts.LogBundle
            ):
        self.artist = artist
        self.log_bundle = log_bundle


    def firebase_to_json(self):
        return {
            "artist": self.artist.firebase_to_json(),
            "log_bundle": self.log_bundle.firebase_to_json()
        }



    # TODO also these methods
    def send_request(self):
        """Sends the request for approval."""

    def approve_request(self):
        """Approves the request."""


class AddRequest(ChangeRequest):
    """Request for adding artists into the database."""


class EditRequest(ChangeRequest):
    """Request for editing an artist in the database."""
