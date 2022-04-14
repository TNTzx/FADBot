"""Contains logic for requests."""


import typing as typ

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import global_vars
import backend.firebase as firebase
import backend.exc_utils as exc_utils
import backend.discord_utils as disc_utils
import backend.logging.loggers as lgr
import backend.other as ot

from .. import artist_lib as art
from .. import vadb_discord_utils
from . import req_struct
from . import req_exts
from . import req_fb_endpoints as req_fb
from . import req_exc


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
            user_sender = global_vars.bot.get_user(int(json.get("user_sender_id"))),
            request_id = json.get("request_id"),
            log_bundle = req_exts.LogBundle.firebase_from_json(json.get("log_bundle"))
        )


    @classmethod
    def firebase_from_id(cls, request_id: int):
        """Gets the `ChangeRequest` from id."""
        all_reqs = firebase.get_data(cls.firebase_get_path(), default = {})

        request_id_str = str(request_id)
        if request_id_str in all_reqs:
            return cls.firebase_from_json(all_reqs[request_id_str])

        raise req_exc.ChangeReqNotFound(f"{cls.firebase_name.capitalize()} request ID {request_id} not found.")


    @classmethod
    def firebase_get_path(cls):
        """Gets the path to the storage of this `ChangeRequest` in Firebase."""
        return firebase.ShortEndpoint.artist_change_reqs.get_path() + [cls.firebase_name]


    @classmethod
    def firebase_get_all_requests(cls):
        """Gets all requests under this `ChangeRequest`."""
        all_reqs_json = firebase.get_data(cls.firebase_get_path(), default = {})
        all_reqs = [cls.firebase_from_json(req_json) for req_json in all_reqs_json]

        if len(all_reqs) == 0:
            raise req_exc.ChangeReqNotFound(f"There are no {cls.type_} requests in Firebase.")

        return all_reqs


    def register_request_id(self):
        """Registers this request with an ID. Sets the `request_id` attribute, also returns the request ID.."""
        request_id: int = firebase.get_data(req_fb.CURRENT_ID.get_path())
        firebase_inc_request_id()
        self.request_id = request_id

        return request_id


    def get_original_artist(self):
        """Gets the original artist from VADB without modifications."""
        return art.Artist.vadb_from_id(self.artist.vadb_info.artist_id)


    async def discord_send_request_pending(self):
        """The discord part of sending the request for approval. Sets the `log_bundle` attribute."""
        self.log_bundle = await req_exts.LogBundle.send_request_pending_logs(self.artist, self.type_, self.request_id)

    def firebase_send_request_pending(self):
        """The Firebase part of sending the request for approval."""
        firebase.edit_data(self.firebase_get_path(), {self.request_id: self.firebase_to_json()})

    async def send_request_pending_intercept(self):
        """An extra method used to intercept the `send_request_pending` method."""

    async def send_request_pending(self, ctx: nx_cmds.Context):
        """Sends the request for approval."""
        await ctx.author.send(f"Sending {self.type_} request...")
        self.register_request_id()
        await self.discord_send_request_pending()
        self.firebase_send_request_pending()

        await self.send_request_pending_intercept()

        await ctx.author.send(
            (
                "Sent request. Please wait for a PA moderator to approve your request.\n"
                f"Request ID: {self.request_id}"
            )
        )

        log_message = (
            f"Request ID [{self.request_id}]: "
            f"{ot.pr_print(self.firebase_to_json())}"
        )
        lgr.log_change_req_data.info(log_message)

        log_message = f"Created request with request ID [{self.request_id}]."
        lgr.log_change_req_changes.info(log_message)


    def firebase_delete_request(self):
        """Deletes the request off of Firebase."""
        if self.request_id is None:
            raise req_exc.ChangeReqNotSubmitted()
        firebase.delete_data(self.firebase_get_path() + [self.request_id])


    async def approve_request(self, ctx: nx_cmds.Context):
        """Approves the request."""

    async def decline_request(self, ctx: nx_cmds.Context):
        """Denies the request."""

    async def set_approval(self, ctx: nx_cmds.Context, is_approved: bool, reason: str = None):
        """Sets the approve status of this request."""
        timeout = global_vars.Timeouts.medium
        self.artist.states.status.value = 0

        artist_embed = vadb_discord_utils.InfoBundle(self.artist).get_embed()


        async def to_approval(approval_cls: req_exts.ApprovalStatus, callback_method: typ.Callable[[nx_cmds.Context], typ.Coroutine[None, None, None]]):
            """Approves / declines the request from an `approval_cls`."""
            # confirmation
            confirm_view = disc_utils.ViewConfirmCancel()

            message_confirm_str = approval_cls.get_message_confirm(
                req_id = self.request_id,
                req_type = self.type_,
                reason = reason
            )
            confirm_str = (
                f"{message_confirm_str}\n"
                f"This command times out in {ot.format_time(timeout)}."
            )
            confirm_message = await ctx.send(
                confirm_str,
                embed = artist_embed,
                view = confirm_view
            )

            final_view = await disc_utils.wait_for_view(ctx, confirm_message, confirm_view)

            if final_view.value == disc_utils.ViewOutputValues.CANCEL:
                raise req_exc.SetApprovalCancelled()


            # processing request
            await ctx.send(approval_cls.get_message_processing(self.type_))

            await callback_method(ctx)

            await ctx.send(
                approval_cls.get_message_complete(
                    req_id = self.request_id,
                    req_type = self.type_,
                    reason = reason
                ),
                embed = artist_embed
            )


            # send logs then append
            new_dump_logs = await req_exts.DumpLogType.send_request_approval_logs(
                approval_cls = approval_cls,
                artist = self.artist,
                req_type = self.type_,
                reason = reason,
                req_id = self.request_id
            )

            self.log_bundle.dump_logs = self.log_bundle.dump_logs + new_dump_logs


            try:
                await self.user_sender.send(
                    approval_cls.get_message_complete_dm(
                        req_id = self.request_id,
                        req_type = self.type_,
                        reason = reason
                    ),
                    embed = artist_embed
                )
            except nx.errors.Forbidden:
                await exc_utils.send_error(
                    ctx,
                    (
                        f"I can't seem to be able to notify the user who sent this request, named `{self.user_sender.name}#{self.user_sender.discriminator}` (ID: `{self.user_sender.id}`).\n"
                        "If you have contacts with this user, please notify them!"
                    )
                )


            # do logging
            log_message = f"Set approval for request ID [{self.request_id}] with approval_cls {approval_cls.__name__}."
            lgr.log_change_req_changes.info(log_message)


        if is_approved:
            await to_approval(req_exts.Approve, self.approve_request)
        else:
            if reason is None:
                raise TypeError("Reason not provided.")

            await to_approval(req_exts.Decline, self.decline_request)


        self.firebase_delete_request()

        await self.log_bundle.delete_live_logs()


    @classmethod
    def get_all_req_types(cls):
        """Gets all `ChangeRequest` subclasses."""
        return cls.__subclasses__()


class AddRequest(ChangeRequest):
    """Request for adding artists into the database."""
    type_ = firebase_name = "add"


    async def approve_request(self, ctx: nx_cmds.Context):
        self.artist.vadb_create_edit()


class EditRequest(ChangeRequest):
    """Request for editing an artist in the database."""
    type_ = firebase_name = "edit"


    async def send_request_pending_intercept(self):
        old_artist = self.get_original_artist()
        old_artist.states.status.value = 2
        old_artist.vadb_edit()


    async def approve_request(self, ctx: nx_cmds.Context):
        self.artist.vadb_edit()

    async def decline_request(self, ctx: nx_cmds.Context):
        old_artist = self.get_original_artist()
        old_artist.states.status.value = 0
        old_artist.vadb_edit()
