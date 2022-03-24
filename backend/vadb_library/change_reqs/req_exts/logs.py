"""Logs for discord."""


import backend.databases.firebase.firebase_interaction as f_i

from ... import discord_utils as disc_utils
from ... import artists as art


LOG_TYPES_INITIAL_PATH = ["artistData", "logTypes"]


class LogType():
    """Parent class for log types."""
    name: str = None
    firebase_name: str = None

    def __init__(self, info_bundles_messages: list[disc_utils.InfoBundleMessages]):
        self.info_bundles_messages = info_bundles_messages


        if not f_i.is_data_exists(LOG_TYPES_INITIAL_PATH + [self.firebase_name]):
            f_i.
    

    @classmethod
    def send_logs(cls, artist: art.Artist):
        """Sends the logs then returns the LogType with all messages."""
        f_i.get_data


class DumpLogs(LogType):
    """Dump logs, used for dumping logs without deleting."""

class LiveLogs(LogType):
    """Live logs, used for dumping logs with deletion after being used."""
