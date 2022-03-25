"""Contains the MessagePointer class."""

# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods


import nextcord as nx

import backend.utils.dataclass as dt
import global_vars.variables as vrs


class MessagePointer(dt.Dataclass):
    """Class that contains channel and message ids to represent a message."""
    def __init__(self, channel_id: int, message_id: int):
        self.channel_id = channel_id
        self.message_id = message_id


    async def get_message(self):
        """Gets the message from discord and returns it."""
        channel: nx.TextChannel = vrs.global_bot.get_channel(int(self.channel_id))
        if channel is None:
            return None
        message: nx.Message = await channel.fetch_message(int(self.message_id))
        if message is None:
            return None

        return message


    def to_json_firebase(self):
        """Returns a dictionary from this `MessagePointer`."""
        return {
            "channelId": str(self.channel_id),
            "messageId": str(self.message_id)
        }

    @classmethod
    def from_json_firebase(cls, data: dict):
        """Returns a `MessagePointer` from the data.
        ```
        {
            "channelId": str
            "messageId": str,
        }
        ```
        """
        return cls(
            channel_id = int(data["channelId"]),
            message_id = int(data["messageId"])
        )


    @classmethod
    def from_message(cls, message: nx.Message):
        """Returns a `MessagePointer` from a message."""
        return cls(
            channel_id = message.channel.id,
            message_id = message.id
        )
