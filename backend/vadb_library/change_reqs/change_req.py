"""Contains logic for requests."""


from .. import artists as art
from . import req_struct
from . import req_exts


# TODO alrighty time to go ham, gonna need logs, accepting and denying requests, etc.
# go ham future tent :patpatpat:

class ChangeRequest(req_struct.RequestStruct):
    """Parent class for all requests."""
    def __init__(
                self,
                artist: art.Artist,
                log_bundle: req_exts.LogBundle
            ):
        self.artist = artist
        self.log_bundle = log_bundle


    # TODO these methods
    def to_json_firebase(self):
        """Returns JSON to send to Firebase."""

    @classmethod
    def from_json_firebase(cls, json: dict):
        """Returns a `ChangeRequest` from the JSON from firebase."""


    # TODO also these methods
    def send_request(self):
        """Sends the request for approval."""

    def approve_request(self):
        """Approves the request."""


class AddRequest(ChangeRequest):
    """Request for adding artists into the database."""


class EditRequest(ChangeRequest):
    """Request for editing an artist in the database."""
