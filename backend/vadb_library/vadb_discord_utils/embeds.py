"""Embed generation."""


import nextcord as nx

import backend.logging.loggers as lgr
import backend.other as ot

from .. import artist_lib as art
from .. import change_reqs
from .. import api


def generate_embed(artist: art.Artist):
    """Generates an `Embed` for this `Artist`."""
    log_message = f"Generating embed for {artist.name}: {ot.pr_print(artist.to_json())}"
    lgr.log_artist_control.info(log_message)

    embed = nx.Embed()

    embed.title = f"Artist data for {artist.name}:"
    embed.description = "_ _"

    id_format = artist.vadb_info.artist_id if artist.vadb_info.artist_id is not None else "Not submitted yet!"


    if (page_link := artist.vadb_info.get_page_link()) is not None:
        emb_url = page_link
    else:
        emb_url = api.consts.BASE_LINK

    embed.set_author(
        name = f"{artist.name} (ID: {id_format})",
        url = emb_url,
        icon_url = artist.details.image_info.avatar.original_url
    )

    if (emb_avatar := artist.details.image_info.avatar.original_url) is not None:
        embed.set_thumbnail(url = emb_avatar)
    if (emb_banner := artist.details.image_info.banner.original_url) is not None:
        embed.set_image(url = emb_banner)

    embed.add_field(name = "Name:", value = f"**{artist.name}**")


    if (temp_aliases := artist.details.aliases.aliases) is not None:
        emb_aliases = f"`{'`, `'.join([alias.name for alias in temp_aliases])}`"
    else:
        emb_aliases = "No aliases!"
    embed.add_field(name = "Aliases:", value = emb_aliases)


    if (temp_desc := artist.details.description) is not None:
        emb_description = temp_desc
    else:
        emb_description = "No description!"
    embed.add_field(name = "Description:", value = emb_description, inline = False)

    if artist.vadb_info.artist_id is not None:
        emb_vadb_page = f"[Click here!]({artist.vadb_info.get_page_link()})"
    else:
        emb_vadb_page = "Artist not submitted yet!"
    embed.add_field(name = "VADB Page:", value = emb_vadb_page, inline = False)


    emb_status = f"**__{artist.states.status.get_name()}__**"
    embed.add_field(name = "Status:", value = emb_status, inline = False)

    emb_availability = f"**__{artist.states.availability.get_name()}__**"
    embed.add_field(name = "Availability:", value = emb_availability)

    if (temp_usage_rights := artist.states.usage_rights.usage_rights) is not None:
        emb_usage_rights_list = []
        for entry in temp_usage_rights:
            emb_usage_rights_list.append(f"{entry.description}: {'Verified' if entry.is_verified else 'Disallowed'}")
        emb_usage_rights = "\n".join(emb_usage_rights_list)
    else:
        emb_usage_rights = "No specific usage rights! Refer to artist's availability."
    embed.add_field(name = "Specific usage rights:", value = f"`{emb_usage_rights}`")


    if (temp_socials := artist.details.socials.socials) is not None:
        emb_socials_list = []
        for entry in temp_socials:
            link_type = entry.get_domain().capitalize()
            emb_socials_list.append(f"[{link_type}]({entry.link})")
        emb_socials = " | ".join(emb_socials_list)
    else:
        emb_socials = "No socials links!"
    embed.add_field(name = "Social links:", value = emb_socials, inline = False)


    if (temp_notes := artist.details.notes) is not None:
        emb_notes = temp_notes
    else:
        emb_notes = "No other notes!"
    embed.add_field(name = "Other notes:", value = emb_notes)


    color_keys = {
        "green": 0x00FF00,
        "red": 0xFF0000,
        "yellow": 0xFFFF00,
        "blue": 0x0000FF
    }
    color_match = ot.Match(color_keys, "green")

    temp_states_val = artist.states.status.value
    temp_avail_var = artist.states.availability.value

    if temp_states_val == 0: # completed
        if temp_avail_var == 0: # verified
            color_match.value = "green"
        elif temp_avail_var == 1: # disallowed
            color_match.value = "red"
        elif temp_avail_var == 2: # contact required
            color_match.value = "yellow"
        elif temp_avail_var == 3: # varies
            color_match.value = "blue"
    elif temp_states_val == 1: # no contact
        color_match.value = "red"
    elif temp_states_val == 2: # pending
        color_match.value = "yellow"

    embed.colour = color_match.get_name()

    return embed


def generate_embed_multiple(
        artists: art.ArtistQuery,
        title: str = None,
        description: str = None,
        footer: str = None
        ):
    """Generates an embed for multiple artists."""
    embed = nx.Embed(
        color = 0xFF0000,
        title = title,
        description = description
    )

    emb_artists = [
        f"**{artist.vadb_info.artist_id}**: {artist.name}"
        for artist in artists.query_items
    ]
    embed.add_field(
        name = "_ _",
        value = "\n".join(emb_artists)
    )

    if footer is not None:
        embed.set_footer(text = footer)

    return embed


def generate_embed_multiple_reqs(
        change_req_query: change_reqs.RequestQuery,
        title: str = None,
        description: str = None,
        footer: str = None
        ):
    """Generates an embed for multiple requests."""
    embed = nx.Embed(
        color = 0xFF0000,
        title = title,
        description = description
    )

    change_req_splits = change_req_query.split_diff_req_types()

    emb_reqs = []

    for change_req_split in change_req_splits:
        emb_req_split = [
            f"\t**{change_req.artist.vadb_info.artist_id}**: {change_req.artist.name}"
            for change_req in change_req_split.query_items
        ]
        emb_req_split = '\n'.join(emb_req_split)

        emb_reqs.append((
            f"{change_req_split.query_items[0].type_.capitalize()} requests:\n"
            f"{emb_req_split}"
        ))

    embed.add_field(
        name = "_ _",
        value = "\n".join(emb_reqs)
    )

    if footer is not None:
        embed.set_footer(text = footer)

    return embed
