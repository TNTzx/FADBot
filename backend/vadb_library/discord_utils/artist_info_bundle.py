"""Defines stuff for showing the information on an artist on Discord."""


import nextcord as nx
import nextcord.ext.commands as cmds

import backend.firebase as firebase
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
        return MessageBundle(message_embed, message_proof)


class MessageBundle(firebase.FBStruct):
    """Stores the information on both the embed and proof messages."""
    def __init__(self, message_pointer_embed: m_p.MessagePointer, message_pointer_proof: m_p.MessagePointer):
        self.message_pointer_embed = message_pointer_embed
        self.message_pointer_proof = message_pointer_proof


    def firebase_to_json(self):
        return {
            "message_pointer_embed": self.message_pointer_embed.firebase_to_json(),
            "message_pointer_proof": self.message_pointer_proof.firebase_from_json()
        }


    def get_messages(self):
        """
        Gets the messages from this `InfoMessageBundle` as a tuple.
        `(message_embed, message_proof)`
        """
        return (self.message_pointer_embed, self.message_pointer_proof)


    async def delete_bundle(self):
        """Deletes this `InfoMessageBundle` from Discord."""
        for message in self.get_messages():
            await message.delete()
