"""Embed generation."""


import nextcord as nx
import nextcord.ext.commands as cmds

import backend.logging.loggers as lgr
import backend.utils.other as mot
import backend.other_functions as o_f

from .. import artist as art


async def generate_embed(artist: art.Artist):
    """Generates an `Embed` for this `Artist`."""
    log_message = f"Generating embed for {artist.name}: {o_f.pr_print(artist.to_json())}"
    lgr.log_artist_control.info(log_message)

    embed = nx.Embed()

    embed.title = f"Artist data for {artist.name}:"
    embed.description = "_ _"

    id_format = artist.vadb_info.artist_id if artist.vadb_info.artist_id is not None else "Not submitted yet!"

    embed.set_author(
        name=f"{artist.name} (ID: {id_format})",
        url=artist.vadb_info.get_page_link(),
        icon_url=artist.details.image_info.avatar.original_url
    )

    embed.set_thumbnail(url=artist.details.image_info.avatar.original_url)
    embed.set_image(url=artist.details.image_info.banner.original_url)

    embed.add_field(name="Name:", value=f"**{artist.name}**")


    if artist.details.aliases.aliases is not None:
        emb_aliases = f"`{'`, `'.join([alias.name for alias in artist.details.aliases.aliases])}`"
    else:
        emb_aliases = "No aliases!"
    embed.add_field(name="Aliases:", value=emb_aliases)


    if artist.details.description is not None:
        emb_description = artist.details.description
    else:
        emb_description = "No description!"
    embed.add_field(name="Description:", value=emb_description, inline=False)

    if artist.vadb_info.artist_id is not None:
        emb_vadb_page = f"[Click here!]({artist.vadb_info.get_page_link()})"
    else:
        emb_vadb_page = "Artist not submitted yet!"
    embed.add_field(name="VADB Page:", value=emb_vadb_page, inline=False)


    emb_status = f"**__{artist.states.status.get_name()}__**"
    embed.add_field(name="Status:", value=emb_status, inline=False)

    emb_availability = f"**__{artist.states.availability.get_name()}__**"
    embed.add_field(name="Availability:", value=emb_availability)

    if artist.states.usage_rights.usage_rights is not None:
        emb_usage_rights_list = []
        for entry in artist.states.usage_rights.usage_rights:
            emb_usage_rights_list.append(f"{entry.description}: {'Verified' if entry.is_verified else 'Disallowed'}")
        emb_usage_rights = "\n".join(emb_usage_rights_list)
    else:
        emb_usage_rights = "No specific usage rights! Refer to artist's availability."
    embed.add_field(name="Specific usage rights:", value=f"`{emb_usage_rights}`")


    if artist.details.socials.socials is not None:
        emb_socials_list = []
        for entry in artist.details.socials.socials:
            link_type = entry.get_domain().capitalize()
            emb_socials_list.append(f"[{link_type}]({entry.link})")
        emb_socials = " | ".join(emb_socials_list)
    else:
        emb_socials = "No socials links!"
    embed.add_field(name="Social links:", value=emb_socials, inline=False)


    if artist.details.notes is not None:
        emb_notes = artist.details.notes
    else:
        emb_notes = "No other notes!"
    embed.add_field(name="Other notes:", value=emb_notes)


    color_keys = {
        "green": 0x00FF00,
        "red": 0xFF0000,
        "yellow": 0xFFFF00,
        "blue": 0x0000FF
    }
    color_match = mot.Match(color_keys, "green")

    if artist.states.status.value == 0: # completed
        if artist.states.availability.value == 0: # verified
            color_match.value = "green"
        elif artist.states.availability.value == 1: # disallowed
            color_match.value = "red"
        elif artist.states.availability.value == 2: # contact required
            color_match.value = "yellow"
        elif artist.states.availability.value == 3: # varies
            color_match.value = "blue"
    elif artist.states.status.value == 1: # no contact
        color_match.value = "red"
    elif artist.states.status.value == 2: # pending
        color_match.value = "yellow"

    embed.colour = color_match.get_name()

    return embed
