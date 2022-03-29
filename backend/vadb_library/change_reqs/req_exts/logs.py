"""Logs for discord."""


import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import backend.firebase as firebase

from ... import discord_utils as disc_utils
from ... import artists as art
from .. import req_exc
from .. import req_struct


def get_log_path(guild: nx.Guild):
    """Gets the path for logs."""
    return ["guildData", str(guild.id), "logs"]


class LogType(req_struct.RequestStruct):
    """Parent class for log types."""
    name: str = None
    firebase_name: str = None

    def __init__(self, info_message_bundles: list[disc_utils.MessageBundle]):
        self.message_bundles = info_message_bundles


    def firebase_to_json(self):
        return [message_bundle.firebase_to_json() for message_bundle in self.message_bundles]



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
        guilds_data: dict = firebase.get_data(["guildData"])
        channel_ids = [guild_data["logs"]["locations"][cls.firebase_name] for guild_data in guilds_data.values()]
        channels = []
        for channel_id in channel_ids:
            if channel_id == firebase.PLACEHOLDER_DATA or \
                    channel_id is None:
                continue

            channel = vrs.global_bot.get_channel(int(channel_id))
            if isinstance(channel, nx.TextChannel):
                channels.append(channel)

        if len(channels) == 0:
            raise req_exc.LogChannelsNotFound(f"Log channels not found for log type \"{cls.name}\".")

        return channels


    @classmethod
    async def send_logs(cls, artist: art.Artist, prefix: str):
        """Sends the logs then returns the LogType with all messages."""
        all_channels = cls.get_all_channels()
        info_artist = disc_utils.InfoBundle(artist)

        message_bundles = []
        for channel in all_channels:
            message_bundle = await info_artist.send_message(channel = channel, prefix = prefix)
            message_bundles.append(message_bundle)

        return cls(info_message_bundles = message_bundles)




class LogTypes():
    """All log types."""
    @classmethod
    def get_all_log_types(cls):
        """Gets all log types."""
        return LogType.__subclasses__()


class DumpLogType(LogType):
    """Dump logs, used for dumping logs without deleting."""
    name = firebase_name = "dump"

class LiveLogType(LogType):
    """Live logs, used for dumping logs with deletion after being used."""
    name = firebase_name = "live"

    async def delete_logs(self):
        """Deletes all logs from discord."""
        for message_bundle in self.message_bundles:
            await message_bundle.delete_bundle()


class LogBundle(req_struct.RequestStruct):
    """Contains all types of logs."""
    def __init__(self, dump_logs: DumpLogType = None, live_logs: LiveLogType = None):
        self.dump_logs = dump_logs
        self.live_logs = live_logs


    def firebase_to_json(self):
        return {
            "dump_logs": self.dump_logs.firebase_to_json(),
            "live_logs": self.live_logs.firebase_to_json()
        }
