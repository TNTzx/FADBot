"""Defines stuff for showing the information on an artist on Discord."""


import colour

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import backend.firebase as firebase
import backend.discord_utils as disc_utils
import backend.logging as lgr
import backend.other as ot

from .. import api
from .. import artist_lib as art


class InfoBundle():
    """Framework for showing information to a discord channel."""
    def __init__(self, artist: art.Artist):
        self.artist = artist


    def get_embed(self):
        """Generates an `Embed` for this `InfoBundle`, usually for the artist."""
        log_message = f"Generating embed for {self.artist.name}: {ot.pr_print(self.artist.to_json())}"
        lgr.log_artist_control.info(log_message)

        embed = nx.Embed()

        embed.title = f"Artist data for {self.artist.name}:"
        embed.description = "_ _"

        id_format = self.artist.vadb_info.artist_id if self.artist.vadb_info.artist_id is not None else "Not submitted yet!"


        if (page_link := self.artist.vadb_info.get_page_link()) is not None:
            emb_url = page_link
        else:
            emb_url = api.consts.BASE_LINK

        embed.set_author(
            name = f"{self.artist.name} (ID: {id_format})",
            url = emb_url,
            icon_url = self.artist.details.image_info.avatar.original_url
        )

        if (emb_avatar := self.artist.details.image_info.avatar.original_url) is not None:
            embed.set_thumbnail(url = emb_avatar)
        if (emb_banner := self.artist.details.image_info.banner.original_url) is not None:
            embed.set_image(url = emb_banner)

        embed.add_field(name = "Name:", value = f"**{self.artist.name}**")


        if (temp_aliases := self.artist.details.aliases.aliases) is not None:
            emb_aliases = f"`{'`, `'.join([alias.name for alias in temp_aliases])}`"
        else:
            emb_aliases = "No aliases!"
        embed.add_field(name = "Aliases:", value = emb_aliases)


        if (temp_desc := self.artist.details.description) is not None:
            emb_description = temp_desc
        else:
            emb_description = "No description!"
        embed.add_field(name = "Description:", value = emb_description, inline = False)

        if self.artist.vadb_info.artist_id is not None:
            emb_vadb_page = f"[Click here!]({self.artist.vadb_info.get_page_link()})"
        else:
            emb_vadb_page = "Artist not submitted yet!"
        embed.add_field(name = "VADB Page:", value = emb_vadb_page, inline = False)


        emb_status = f"**__{self.artist.states.status.get_name()}__**"
        embed.add_field(name = "Status:", value = emb_status, inline = False)

        emb_availability = f"**__{self.artist.states.availability.get_name()}__**"
        embed.add_field(name = "Availability:", value = emb_availability)

        if (temp_usage_rights := self.artist.states.usage_rights.usage_rights) is not None:
            emb_usage_rights_list = []
            for entry in temp_usage_rights:
                emb_usage_rights_list.append(f"{entry.description}: {'Verified' if entry.is_verified else 'Disallowed'}")
            emb_usage_rights = "\n".join(emb_usage_rights_list)
        else:
            emb_usage_rights = "No specific usage rights! Refer to artist's availability."
        embed.add_field(name = "Specific usage rights:", value = f"`{emb_usage_rights}`")


        if (temp_socials := self.artist.details.socials.socials) is not None:
            emb_socials_list = []
            for entry in temp_socials:
                link_type = entry.get_domain().capitalize()
                emb_socials_list.append(f"[{link_type}]({entry.link})")
            emb_socials = " | ".join(emb_socials_list)
        else:
            emb_socials = "No socials links!"
        embed.add_field(name = "Social links:", value = emb_socials, inline = False)


        if (temp_notes := self.artist.details.notes) is not None:
            emb_notes = temp_notes
        else:
            emb_notes = "No other notes!"
        embed.add_field(name = "Other notes:", value = emb_notes)


        temp_states_val = self.artist.states.status.value
        temp_avail_var = self.artist.states.availability.value

        if temp_states_val == 1: # no contact
            selected_color = colour.Color("red")
        else:
            if temp_avail_var == 0: # verified
                selected_color = colour.Color("#00FF00")
            elif temp_avail_var == 1: # disallowed
                selected_color = colour.Color("#FF0000")
            elif temp_avail_var == 2: # contact required
                selected_color = colour.Color("#FFFF00")
            elif temp_avail_var == 3: # varies
                selected_color = colour.Color("#0000FF")


        if temp_states_val == 2: # pending
            selected_color.set_luminance(selected_color.get_luminance() / 2)

        embed.colour = int(selected_color.get_hex_l()[1:], base = 16)

        return embed


    async def send_message(self, channel: nx_cmds.Context | nx.TextChannel | nx.DMChannel, prefix: str = None, view: disc_utils.View = None):
        """Sends the message to a text channel. The view is attached to `message_proof`."""
        message_embed = await channel.send(prefix, embed = self.get_embed())
        message_proof = await channel.send(self.artist.proof.original_url, view = view)
        return MessageBundle(
            message_pointer_embed = disc_utils.MessagePointer.from_message(message_embed),
            message_pointer_proof = disc_utils.MessagePointer.from_message(message_proof)
        )


class MessageBundle(firebase.FBStruct):
    """Stores the information on both the embed and proof messages."""
    def __init__(self, message_pointer_embed: disc_utils.MessagePointer, message_pointer_proof: disc_utils.MessagePointer):
        self.message_pointer_embed = message_pointer_embed
        self.message_pointer_proof = message_pointer_proof


    def firebase_to_json(self):
        return {
            "message_pointer_embed": self.message_pointer_embed.firebase_to_json(),
            "message_pointer_proof": self.message_pointer_proof.firebase_to_json()
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        def pointer_from_json(key: str):
            return disc_utils.MessagePointer.firebase_from_json(json.get(key))

        return cls(
            message_pointer_embed = pointer_from_json("message_pointer_embed"),
            message_pointer_proof = pointer_from_json("message_pointer_proof")
        )


    def get_messages(self):
        """
        Gets the messages from this `InfoMessageBundle` as a tuple.
        `(message_embed, message_proof)`
        """
        return (self.message_pointer_embed, self.message_pointer_proof)


    async def delete_bundle(self):
        """Deletes this `InfoMessageBundle` from Discord."""
        for message in self.get_messages():
            await message.delete_message()
