"""Log library for logging."""

# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=useless-super-delegation
# pylint: disable=unused-import
# pylint: disable=invalid-name

from __future__ import annotations
import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import backend.main_library.dataclass as dt
import backend.main_library.message_pointer as m_p
import backend.databases.firebase.firebase_interaction as f_i


class LogTypes:
    """Class that contains log types."""
    class Base:
        """Base class."""
        def __init__(self):
            self.path: list[str] = None
            self.title_str: str = None

    class Pending(Base):
        """For pending artist submissions."""
        def __init__(self):
            super().__init__()
            self.path = ["artistData", "pending", "data"]
            self.title_str = "A new pending artist submission has been created."
    PENDING = Pending()

    class Editing(Base):
        """For editing requests."""
        def __init__(self):
            super().__init__()
            self.path = ["artistData", "editing", "data"]
            self.title_str = "A new edit request has been created."

    EDITING = Editing()


class LogChannelTypes:
    """Class for containing log channel types."""

    class Base:
        """Base class for log channel types."""
        PATH_ADD: str = ""
        PATH_BASE = ["logs", "locations"]
        def __init__(self):
            self.path_full = self.PATH_BASE + [self.PATH_ADD]

        def get_all_channels(self):
            """Gets all channels from all servers in this LogChannelType."""
            log_channels: list[nx.TextChannel] = []
            guild_datas = f_i.get_data(["guildData"])

            for guild_data in guild_datas.values():
                log_channel_id = guild_data["logs"]["locations"][self.PATH_ADD]

                if log_channel_id == vrs.PLACEHOLDER_DATA:
                    continue

                log_channel = vrs.global_bot.get_channel(int(log_channel_id))
                if log_channel is None:
                    continue

                log_channels.append(log_channel)

            if len(log_channels) == 0:
                return None
            return log_channels


    class Dump(Base):
        """Logs where everything is kept."""
        PATH_ADD = "dump"

    DUMP = Dump()

    class Live(Base):
        """Logs where only pending requests are kept."""
        PATH_ADD = "live"

    LIVE = Live()



class Log(dt.DataclassSub):
    """A data structure to store a log.
    "message": LogMessages
    "user_id": int"""
    def __init__(self, datas: dict = None):
        self.message = self.LogMessages()
        self.user_id = None

    class LogMessages(dt.DataclassSub):
        """A data structure to store messages of a log.
        "main": m_p.MessagePointer
        "proof": m_p.MessagePointer"""
        def __init__(self, datas: dict[str, m_p.MessagePointer] = None):
            self.main = m_p.MessagePointer()
            self.proof = m_p.MessagePointer()
