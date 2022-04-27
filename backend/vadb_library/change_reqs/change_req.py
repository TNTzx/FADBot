"""Contains logic for requests."""


import typing as typ

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import global_vars
import backend.firebase as firebase
import backend.exc_utils as exc_utils
import backend.discord_utils as disc_utils
import backend.logging as lgr
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
    req_type: str = None
    firebase_name: str = None

    def __init__(
            self,
            req_info: req_exts.ChangeReqInfo,
            log_bundle: req_exts.LogBundle = req_exts.LogBundle()
            ):
        self.req_info = req_info
        self.log_bundle = log_bundle


    def __init_subclass__(cls) -> None:
        path = cls.firebase_get_path()
        if not firebase.is_data_exists(path):
            firebase.override_data(path, firebase.PLACEHOLDER_DATA)


    def firebase_to_json(self):
        return {
            "req_info": self.req_info.firebase_to_json(),
            "log_bundle": self.log_bundle.firebase_to_json()
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        return cls(
            req_info = req_exts.ChangeReqInfo.firebase_from_json(json.get("req_info")),
            log_bundle = req_exts.LogBundle.firebase_from_json(json.get("log_bundle"))
        )


    @classmethod
    def firebase_from_id(cls, request_id: int):
        """Gets the `ChangeRequest` from id."""
        all_reqs_json = firebase.get_data(cls.firebase_get_path(), default = {})

        all_reqs = [cls.firebase_from_json(req_json) for req_json in all_reqs_json]
        for req in all_reqs:
            if req.req_info.request_id == request_id:
                return req

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
            raise req_exc.ChangeReqNotFound(f"There are no {cls.req_type} requests in Firebase.")

        return all_reqs


    def register_request_id(self):
        """Registers this request with an ID. Sets the `request_id` attribute, also returns the request ID.."""
        request_id: int = firebase.get_data(req_fb.CURRENT_ID.get_path())
        firebase_inc_request_id()
        self.req_info.request_id = request_id

        return request_id


    def get_original_artist(self):
        """Gets the original artist from VADB without modifications."""
        return art.Artist.vadb_from_id(self.req_info.artist.vadb_info.artist_id)


    async def discord_send_request_pending(self):
        """The discord part of sending the request for approval. Sets the `log_bundle` attribute."""
        self.log_bundle = await req_exts.LogBundle.send_request_pending_logs(self.req_info, self.req_type)

    def firebase_send_request_pending(self):
        """The Firebase part of sending the request for approval."""
        firebase.append_data(self.firebase_get_path(), [self.firebase_to_json()])

    async def send_request_pending_intercept(self):
        """An extra method used to intercept the `send_request_pending` method."""

    async def send_request_pending(self, channel: nx.TextChannel):
        """Sends the request for approval."""
        self.req_info.artist.states.status.value = 2

        await channel.send(f"Sending {self.req_type} request...")
        self.register_request_id()
        await self.discord_send_request_pending()
        self.firebase_send_request_pending()

        await self.send_request_pending_intercept()

        await channel.send(
            "Sent request. Please wait for a PA moderator to approve your request.\n",
            embed = self.req_info.get_embed()
        )

        log_message = (
            f"Request ID [{self.req_info.request_id}]: "
            f"{ot.pr_print(self.firebase_to_json())}"
        )
        lgr.log_change_req_data.info(log_message)

        log_message = f"Created request with request ID [{self.req_info.request_id}]."
        lgr.log_change_req_changes.info(log_message)


    def firebase_delete_request(self):
        """Deletes the request off of Firebase."""
        if self.req_info.request_id is None:
            raise req_exc.ChangeReqNotSubmitted()
        firebase.delete_data(self.firebase_get_path() + [self.req_info.request_id])


    async def approve_request(self, channel: nx.TextChannel, author: nx.User):
        """Approves the request."""

    async def decline_request(self, channel: nx.TextChannel, author: nx.User):
        """Denies the request."""

    async def set_approval(self, channel: nx.TextChannel, author: nx.User, is_approved: bool, reason: str = None):
        """Sets the approve status of this request."""
        timeout = global_vars.Timeouts.medium

        req_embed = self.req_info.get_embed()


        async def to_approval(approval_cls: req_exts.ApprovalStatus, callback_method: typ.Callable[[nx.TextChannel, nx.User], typ.Coroutine[None, None, None]]):
            """Approves / declines the request from an `approval_cls`."""
            # confirmation
            confirm_view = disc_utils.ViewConfirmCancel()

            message_confirm_str = approval_cls.get_message_confirm(
                req_type = self.req_type,
                reason = reason
            )
            confirm_str = (
                f"{message_confirm_str}\n"
                f"This command times out in {ot.format_time(timeout)}."
            )
            confirm_message = await channel.send(
                confirm_str,
                embed = req_embed,
                view = confirm_view
            )

            final_view = await disc_utils.wait_for_view(
                channel = channel,
                author = author,
                original_message = confirm_message,
                view = confirm_view
            )

            if final_view.value == disc_utils.ViewOutputValues.CANCEL:
                raise req_exc.SetApprovalCancelled()


            # processing request
            self.req_info.artist.states.status.value = 0

            new_req_embed = self.req_info.get_embed()

            await channel.send(approval_cls.get_message_processing(self.req_type))
            await callback_method(channel, author)
            await channel.send(
                approval_cls.get_message_complete(
                    req_type = self.req_type,
                    reason = reason
                ),
                embed = new_req_embed
            )


            # send logs then append
            new_dump_logs = await req_exts.DumpLogType.send_request_approval_logs(
                approval_cls = approval_cls,
                reason = reason,
                req_info = self.req_info,
                req_type = self.req_type
            )

            self.log_bundle.dump_logs = self.log_bundle.dump_logs + new_dump_logs


            try:
                await self.req_info.user_sender.send(
                    approval_cls.get_message_complete_dm(
                        req_type = self.req_type,
                        reason = reason
                    ),
                    embed = new_req_embed
                )
            except nx.errors.Forbidden:
                await exc_utils.SendWarn(
                    error_place = exc_utils.ErrorPlace(channel, author),
                    suffix = (
                        f"I can't seem to be able to notify the user who sent this request, named `{self.req_info.user_sender.name}#{self.req_info.user_sender.discriminator}` (ID: `{self.req_info.user_sender.id}`).\n"
                        "If you have contacts with this user, please notify them!"
                    )
                ).send()


            # do logging
            log_message = f"Set approval for request ID [{self.req_info.request_id}] with approval_cls {approval_cls.__name__}."
            lgr.log_change_req_changes.info(log_message)


        if is_approved:
            await to_approval(req_exts.Approve, self.approve_request)
        else:
            if reason is None:
                raise req_exc.SetApprovalNoReason()

            await to_approval(req_exts.Decline, self.decline_request)


        self.firebase_delete_request()

        await self.log_bundle.delete_live_logs()


    @classmethod
    def get_all_req_types(cls):
        """Gets all `ChangeRequest` subclasses."""
        return cls.__subclasses__()


class AddRequest(ChangeRequest):
    """Request for adding artists into the database."""
    req_type = firebase_name = "add"


    async def approve_request(self, channel: nx.TextChannel, author: nx.User):
        self.req_info.artist.vadb_create_edit()


class EditRequest(ChangeRequest):
    """Request for editing an artist in the database."""
    req_type = firebase_name = "edit"


    async def send_request_pending_intercept(self):
        old_artist = self.get_original_artist()
        old_artist.states.status.value = 2
        old_artist.vadb_edit()


    async def approve_request(self, channel: nx.TextChannel, author: nx.User):
        self.req_info.artist.states.status.value = 0
        self.req_info.artist.vadb_edit()

    async def decline_request(self, channel: nx.TextChannel, author: nx.User):
        old_artist = self.get_original_artist()
        old_artist.states.status.value = 0
        old_artist.vadb_edit()
