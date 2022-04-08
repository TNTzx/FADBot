"""Contains the MessagePointer class."""


import nextcord as nx

import backend.firebase as firebase

import global_vars


class MessagePointer(firebase.FBStruct):
    """Class that contains channel and message ids to represent a message."""
    def __init__(self, channel_id: int, message_id: int):
        self.channel_id = channel_id
        self.message_id = message_id


    def firebase_to_json(self):
        return {
            "channel_id": str(self.channel_id),
            "message_id": str(self.message_id)
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        return cls(
            channel_id = int(json.get("channel_id")),
            message_id = int(json.get("message_id"))
        )


    @classmethod
    def from_message(cls, message: nx.Message):
        """Returns a `MessagePointer` from a message."""
        return cls(
            channel_id = message.channel.id,
            message_id = message.id
        )


    async def get_message(self):
        """Gets the message from discord and returns it."""
        channel: nx.TextChannel = global_vars.global_bot.get_channel(int(self.channel_id))
        if channel is None:
            return None
        message: nx.Message = await channel.fetch_message(int(self.message_id))
        if message is None:
            return None

        return message


    async def delete_message(self):
        """Deletes this message."""
        message = await self.get_message()
        await message.delete()
