"""Defines stuff for showing the information on an artist on Discord."""


import nextcord as nx
import nextcord.ext.commands as cmds

import backend.utils.message_pointer as m_p
import backend.utils.views as vw

from .. import artists as art
from . import embeds


class InfoBundle():
    """Framework for showing information to a discord channel."""
    def __init__(self, artist: art.Artist):
        self.artist = artist


    def get_embed(self):
        """Gets the embed of the artist."""
        return embeds.generate_embed(self.artist)


    async def send_message(self, channel: cmds.Context | nx.TextChannel | nx.DMChannel, prefix: str = None, view: vw.View = None):
        """Sends the message to a text channel. The view is attached to `message_proof`."""
        message_embed = await channel.send(prefix, embed = self.get_embed())
        message_proof = await channel.send(self.artist.proof.original_url, view = view)
        return InfoMessageBundle(message_embed, message_proof)


class InfoMessageBundle():
    """Stores the information on both the embed and proof messages."""
    def __init__(self, message_embed: nx.Message, message_proof: nx.Message):
        self.message_embed = message_embed
        self.message_proof = message_proof


    def to_data_firebase(self):
        """Returns a dictionary for this `InfoMessageBundle`."""
        return {
            "message_embed_pointer": m_p.MessagePointer.from_message(self.message_embed).to_data_firebase(),
            "message_proof_pointer": m_p.MessagePointer.from_message(self.message_proof).to_data_firebase()
        }


    @classmethod
    async def from_data_firebase(cls, data: dict):
        """Returns an `InfoMessageBundle` for the data.
        ```
        {
            "message_embed_pointer": MessagePointer(),
            "message_proof_pointer": MessagePointer()
        }
        ```
        """
        async def pointer_from_data(pointer_json: dict):
            return await m_p.MessagePointer.from_data_firebase(pointer_json).get_message()

        return cls(
            message_embed = await pointer_from_data(data["message_embed_pointer"]),
            message_proof = await pointer_from_data(data["message_proof_pointer"])
        )
