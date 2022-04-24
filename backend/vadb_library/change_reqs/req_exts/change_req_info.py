"""Contains logic for change request info."""


import nextcord as nx
import nextcord.ext.commands as nx_cmds

import global_vars
import backend.discord_utils as disc_utils

from ... import artist_lib
from ... import vadb_discord_utils
from .. import req_struct


class ChangeReqInfo(req_struct.ChangeRequestStructure):
    """Represents information on a change request."""
    def __init__(
            self,
            artist: artist_lib.Artist,
            user_sender: nx.User,
            request_id: int = None,
        ):
        self.artist = artist
        self.user_sender = user_sender
        self.request_id = request_id


    def firebase_to_json(self):
        return {
            "artist": self.artist.firebase_to_json(),
            "user_sender_id": str(self.user_sender.id),
            "request_id": self.request_id,
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        return cls(
            artist = artist_lib.Artist.firebase_from_json(json.get("artist")),
            user_sender = global_vars.bot.get_user(int(json.get("user_sender_id"))),
            request_id = json.get("request_id"),
        )


    def get_embed(self):
        """Generates the embed of this `ReqInfo`."""
        embed = vadb_discord_utils.InfoBundle(self.artist).get_embed()

        embed.insert_field_at(0, name = disc_utils.make_horizontal_rule(left_text = "ARTIST DATA"), value = disc_utils.INVISIBLE_CHAR)
        disc_utils.make_horizontal_rule_field(embed, left_text = "REQUEST DATA")

        emb_req_id = str(self.request_id) if self.request_id is not None else "Request not submitted yet!"
        embed.add_field(
            name = "Request ID:",
            value = emb_req_id
        )

        emb_user_sender = f"{self.user_sender.name}#{self.user_sender.discriminator}"

        embed.add_field(
            name = "Request Creator:",
            value = emb_user_sender
        )

        return embed


    async def discord_send_message(self, channel: nx_cmds.Context | nx.TextChannel | nx.DMChannel, prefix: str = None, view: disc_utils.View = None):
        """Sends the message to a text channel. The view is attached to `message_proof`."""
        message_embed = await channel.send(prefix, embed = self.get_embed())
        message_proof = await channel.send(self.artist.proof.original_url, view = view)
        return vadb_discord_utils.MessageBundle(
            message_pointer_embed = disc_utils.MessagePointer.from_message(message_embed),
            message_pointer_proof = disc_utils.MessagePointer.from_message(message_proof)
        )
