"""Contains logic for request info bundles."""


import nextcord as nx
import nextcord.ext.commands as nx_cmds

import backend.discord_utils as disc_utils

from .. import vadb_discord_utils
from . import change_req


class ReqInfoBundle():
    """Represents a request info bundle."""
    def __init__(self, change_req: change_req.ChangeRequest):
        self.change_req = change_req


    async def send_message(self, channel: nx_cmds.Context | nx.TextChannel | nx.DMChannel, prefix: str = None, view: disc_utils.View = None):
        """Sends the message to a text channel. The view is attached to `message_proof`."""
        message_embed = await channel.send(prefix, embed = self.change_req.generate_embed())
        message_proof = await channel.send(self.change_req.artist.proof.original_url, view = view)
        return vadb_discord_utils.MessageBundle(
            message_pointer_embed = disc_utils.MessagePointer.from_message(message_embed),
            message_pointer_proof = disc_utils.MessagePointer.from_message(message_proof)
        )
