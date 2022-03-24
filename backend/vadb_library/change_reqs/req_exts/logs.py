"""Logs for discord."""


import nextcord as nx

import backend.firebase as firebase

from ... import discord_utils as disc_utils
from ... import artists as art


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
        """Sets the guild's channel as this LogType."""
        firebase.override_data(get_log_path(guild) + ["locations", cls.firebase_name], str(channel.id))

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


class DumpLogs(LogType):
    """Dump logs, used for dumping logs without deleting."""

class LiveLogs(LogType):
    """Live logs, used for dumping logs with deletion after being used."""
