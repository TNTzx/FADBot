"""Contains the MessagePointer class."""

# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods


import nextcord as nx

import backend.main_library.dataclass as dt
import global_vars.variables as vrs


class MessagePointer(dt.Dataclass):
    """Class that contains channel and message ids to represent a message."""
    def __init__(self, datas: dict = None, channel_id = "0", message_id = "0"):
        if datas is None:
            datas = {
                "channel_id": channel_id,
                "message_id": message_id
            }
        self.channel_id = str(datas["channel_id"])
        self.message_id = str(datas["message_id"])

    async def get_message(self):
        """Gets the message from discord and returns it."""
        channel: nx.TextChannel = vrs.global_bot.get_channel(int(self.channel_id))
        if channel is None:
            return None
        message: nx.Message = await channel.fetch_message(int(self.message_id))
        if message is None:
            return None

        return message
