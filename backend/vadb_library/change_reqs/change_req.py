"""Contains logic for requests."""


import nextcord as nx
import nextcord.ext.commands as cmds

import backend.firebase as firebase
import global_vars.variables as vrs

from .. import artists as art
from . import req_struct
from . import req_exts
from . import req_fb_endpoints as req_fb


def firebase_inc_request_id():
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
            user_sender: nx.User,
            request_id: int = None,
            log_bundle: req_exts.LogBundle = req_exts.LogBundle()
            ):
        self.artist = artist
        self.user_sender = user_sender
        self.request_id = request_id
        self.log_bundle = log_bundle


    def __init_subclass__(cls) -> None:
        path = cls.firebase_get_path()
        if not firebase.is_data_exists(path):
            firebase.override_data(path, firebase.PLACEHOLDER_DATA)


    def firebase_to_json(self):
        return {
            "artist": self.artist.firebase_to_json(),
            "user_sender_id": str(self.user_sender.id),
            "request_id": self.request_id,
            "log_bundle": self.log_bundle.firebase_to_json()
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        return cls(
            artist = art.Artist.firebase_from_json(json.get("artist")),
            user_sender = vrs.global_bot.get_user(int(json.get("user_sender_id"))),
            request_id = json.get("request_id"),
            log_bundle = req_exts.LogBundle.firebase_from_json(json.get("log_bundle"))
        )


    @classmethod
    def firebase_get_path(cls):
        """Gets the path to the storage of this `ChangeRequest` in Firebase."""
        return firebase.ShortEndpoint.artist_change_reqs.get_path() + [cls.firebase_name]


    async def discord_send_request_pending(self):
        """The discord part of sending the request for approval. Sets the `log_bundle` attribute."""
        self.log_bundle = await req_exts.LogBundle.send_request_pending_logs(self.artist, self.type_)

    def firebase_send_request_pending(self):
        """The Firebase part of sending the request for approval. Sets the `request_id` attribute."""
        request_id = firebase.get_data(req_fb.CURRENT_ID.get_path())
        firebase_inc_request_id()
        self.request_id = request_id
        firebase.edit_data(self.firebase_get_path(), {request_id: self.firebase_to_json()})

    async def send_request_pending(self, ctx: cmds.Context):
        """Sends the request for approval."""
        await ctx.author.send(f"Sending {self.type_} request...")
        await self.discord_send_request_pending()
        self.firebase_send_request_pending()
        await ctx.author.send("Sent request. Please wait for a PA moderator to approve your request.")


    def approve_request(self):
        """Approves the request."""


class AddRequest(ChangeRequest):
    """Request for adding artists into the database."""
    type_ = firebase_name = "add"


class EditRequest(ChangeRequest):
    """Request for editing an artist in the database."""
    type_ = firebase_name = "edit"
