"""Logs for discord."""


import nextcord as nx

import global_vars.variables as vrs
import backend.firebase as firebase

from ... import discord_utils as disc_utils
from ... import artists as art
from .. import req_exc


def get_log_path(guild: nx.Guild):
    """Gets the path for logs."""
    return ["guildData", str(guild.id), "logs"]


class LogType():
    """Parent class for log types."""
    name: str = None
    firebase_name: str = None

    def __init__(self, info_bundles_messages: list[disc_utils.InfoBundleMessages]):
        self.info_bundles_messages = info_bundles_messages


    @classmethod
    def set_channel(cls, guild: nx.Guild, channel: nx.TextChannel):
        """Sets the guild's channel as this `LogType`."""
        firebase.override_data(get_log_path(guild) + ["locations", cls.firebase_name], str(channel.id))

    @classmethod
    def get_all_channels(cls):
        """Gets all channels from each guild in this `LogType`."""
        guilds_data: dict = firebase.get_data(["guildData"])
        channel_ids = [guild_data["logs"]["locations"][cls.firebase_name] for guild_data in guilds_data.values()]
        channels = []
        for channel_id in channel_ids:
            if channel_id == firebase.PLACEHOLDER_DATA:
                continue

            channel = vrs.global_bot.get_channel(int(channel_id))
            if isinstance(channel, nx.TextChannel):
                channels.append(channel)

        if len(channels) == 0:
            raise req_exc.LogChannelsNotFound(f"Log channels not found for log type \"{cls.name}\".")

        return channels


    # TODO send logs
    @classmethod
    def send_logs(cls, artist: art.Artist):
        """Sends the logs then returns the LogType with all messages."""



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
