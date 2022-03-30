"""Contains logic for requests."""


import backend.firebase as firebase

from .. import artists as art
from . import req_struct
from . import req_exts
from . import req_fb_endpoints as req_fb
from . import req_exc


def firebase_inc_request_id(self):
    """Increments the request ID by one."""
    path = req_fb.CURRENT_ID.get_path()
    current_id = firebase.get_data(path)
    current_id += 1
    firebase.override_data(path, current_id)


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


    def __init_subclass__(cls) -> None:
        path = cls.firebase_get_path()
        if not firebase.is_data_exists(path):
            firebase.override_data(path, firebase.PLACEHOLDER_DATA)


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


    @classmethod
    def firebase_get_path(cls):
        """Gets the path to the storage of this `ChangeRequest` in Firebase."""
        return firebase.ShortEndpoint.artist_change_reqs.get_path() + [cls.firebase_name]


    async def discord_send_request_pending(self):
        """The discord part of sending the request for approval."""
        self.log_bundle = await req_exts.LogBundle.send_request_pending_logs(self.artist, self.type_)

    async def firebase_send_request_pending(self):
        """The Firebase part of sending the request for approval."""
        artist_id = self.artist.vadb_info.artist_id
        if artist_id is None:
            raise req_exc.ChangeReqNotVADBSubmitted()

        firebase.edit_data(self.firebase_get_path(), {artist_id: self.firebase_to_json()})

    async def send_request_pending(self):
        """Sends the request for approval."""


    def approve_request(self):
        """Approves the request."""


class AddRequest(ChangeRequest):
    """Request for adding artists into the database."""
    type_ = firebase_name = "add"


class EditRequest(ChangeRequest):
    """Request for editing an artist in the database."""
    type_ = firebase_name = "edit"
