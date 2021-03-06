"""Logs for discord."""


from __future__ import annotations

import typing as typ

import nextcord as nx

import global_vars
import backend.firebase as firebase

from ... import vadb_discord_utils as vadb_disc_utils
from .. import req_exc
from .. import req_struct
from . import approve_status
from . import change_req_info


def get_log_path(guild: nx.Guild):
    """Gets the path for logs."""
    return firebase.ENDPOINTS.e_discord.e_guilds.get_path() + [str(guild.id), "logs"]


class LogType(req_struct.ChangeRequestStructure):
    """Parent class for log types."""
    name: str = None
    firebase_name: str = None

    def __init__(
            self,
            message_bundles: list[vadb_disc_utils.MessageBundle] = None
        ):
        self.message_bundles = message_bundles

    def __add__(self, other: LogType):
        return self.__class__(
            message_bundles = self.message_bundles + other.message_bundles
        )


    def firebase_to_json(self):
        if self.message_bundles is None:
            return None

        return [message_bundle.firebase_to_json() for message_bundle in self.message_bundles]

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        if json is None:
            return cls()

        return cls(
            message_bundles = [
                vadb_disc_utils.MessageBundle.firebase_from_json(message_bundle_json)
                for message_bundle_json in json
            ]
        )



    @classmethod
    def set_channel(cls, guild: nx.Guild, channel: nx.TextChannel):
        """Sets the guild's channel as this `LogType`."""
        main_path = get_log_path(guild) + ["locations", cls.firebase_name]
        if channel.id == int(firebase.get_data(main_path)):
            raise req_exc.LogChannelAlreadySet(f"Log channel \"{channel.name}\" already set for guild id {guild.id}.")
        firebase.override_data(main_path, str(channel.id))

    @classmethod
    def get_all_channels(cls) -> list[nx.TextChannel] | None:
        """Gets all channels from each guild in this `LogType`."""
        guilds_data: dict = firebase.get_data(firebase.ENDPOINTS.e_discord.e_guilds.get_path())
        channel_ids = [guild_data["logs"]["locations"][cls.firebase_name] for guild_data in guilds_data.values()]
        channels = []
        for channel_id in channel_ids:
            if channel_id == firebase.PLACEHOLDER_DATA or \
                    channel_id is None:
                continue

            channel = global_vars.bot.get_channel(int(channel_id))
            if isinstance(channel, nx.TextChannel):
                channels.append(channel)

        if len(channels) == 0:
            raise req_exc.LogChannelsNotFound(f"Log channels not found for log type \"{cls.name}\".")

        return channels


    @classmethod
    async def send_logs(cls, prefix: str, req_info: change_req_info.ChangeReqInfo, req_type: str):
        """Sends the logs then returns the LogType with all messages."""
        all_channels = cls.get_all_channels()

        message_bundles = []
        for channel in all_channels:
            try:
                message_bundle = await req_info.discord_send_message(
                    channel = channel,
                    prefix = prefix
                )
            except nx.errors.Forbidden:
                continue

            message_bundles.append(message_bundle)

        return cls(message_bundles = message_bundles)


    @classmethod
    async def send_request_pending_logs(cls, req_info: change_req_info.ChangeReqInfo, req_type: str):
        """Sends the logs to the channels in this `LogType` then returns this `LogType`."""
        return await cls.send_logs(
            f"This {req_type} request is being processed. Please wait for this request to be approved.\n",
            req_info = req_info, req_type = req_type
        )




class LogTypes():
    """All log types."""
    @classmethod
    def get_all_log_types(cls):
        """Gets all log types."""
        return LogType.__subclasses__()


class DumpLogType(LogType):
    """Dump logs, used for dumping logs without deleting."""
    name = firebase_name = "dump"

    @classmethod
    async def send_request_approval_logs(
            cls,
            approval_cls: typ.Type[approve_status.ApprovalStatus],
            reason: str,
            req_info: change_req_info.ChangeReqInfo,
            req_type: str
            ):
        """Sends the approved / declined logs to this `DumpLogType`."""
        return await cls.send_logs(
            prefix = approval_cls.get_message_complete_dump_logs(
                req_type = req_type,
                reason = reason
            ),
            req_info = req_info,
            req_type = req_type
        )


class LiveLogType(LogType):
    """Live logs, used for dumping logs with deletion after being used."""
    name = firebase_name = "live"

    async def delete_logs(self):
        """Deletes all logs from discord."""
        for message_bundle in self.message_bundles:
            await message_bundle.delete_bundle()


class LogBundle(req_struct.ChangeRequestStructure):
    """Contains all types of logs."""
    def __init__(self, dump_logs: DumpLogType = None, live_logs: LiveLogType = None):
        self.dump_logs = dump_logs
        self.live_logs = live_logs


    def firebase_to_json(self):
        return {
            "dump_logs": self.dump_logs.firebase_to_json(),
            "live_logs": self.live_logs.firebase_to_json()
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        return cls(
            dump_logs = DumpLogType.firebase_from_json(json.get("dump_logs")),
            live_logs = LiveLogType.firebase_from_json(json.get("live_logs"))
        )


    @classmethod
    async def send_request_pending_logs(cls, req_info: change_req_info.ChangeReqInfo, req_type: str):
        """Sends the logs to these log types then returns a `LogBundle` of these messages."""
        async def call_send(log_type: typ.Type[LogType]):
            """Calls `send_request_pending_logs` for the `LogType` and returns its result."""
            return await log_type.send_request_pending_logs(req_info, req_type)

        return cls(
            dump_logs = await call_send(DumpLogType),
            live_logs = await call_send(LiveLogType)
        )


    async def delete_live_logs(self):
        """Deletes the live logs. Used when approving an artist."""
        if self.live_logs is None:
            return

        await self.live_logs.delete_logs()
        self.live_logs = None
