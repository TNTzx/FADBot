"""Defines stuff for showing the information on an artist on Discord."""


import nextcord as nx
import nextcord.ext.commands as cmds

from .. import artist_structs as art
from . import embeds


class InfoBundle():
    """Framework for showing information to a discord channel."""
    def __init__(self, artist: art.Artist):
        self.artist = artist


    def get_embed(self):
        """Gets the embed of the artist."""
        return embeds.generate_embed(self.artist)


    async def send_message(self, channel: cmds.Context | nx.TextChannel | nx.DMChannel, prefix: str = None):
        """Sends the message to a text channel."""
        message_embed = await channel.send(prefix, embed = self.get_embed())
        message_proof = await channel.send(self.artist.proof.original_url)
        return InfoBundleMessages(message_embed, message_proof)


class InfoBundleMessages():
    """Stores the information on both the embed and proof messages."""
    def __init__(self, message_embed: nx.Message, message_proof: nx.Message):
        self.message_embed = message_embed
        self.message_proof = message_proof
