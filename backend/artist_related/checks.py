"""Contains checks and logic for artist parsing."""

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-statements
# pylint: disable=line-too-long
# pylint: disable=unused-argument


import requests as req
# import nextcord as nx
import nextcord.ext.commands as cmds

import backend.artist_related.library.artist_library as a_l
import backend.exceptions.custom_exc as c_e
import backend.exceptions.send_error as s_e


async def get_artist_by_id(ctx: cmds.Context, artist_id: int) -> a_l.Default:
    """Gets an artist from its id. Sends an error if not found."""
    try:
        artist: a_l.Default = a_l.get_artist_by_id_vadb(artist_id)
        artist.get_logs()
        return artist
    except req.exceptions.HTTPError as exc:
        await s_e.send_error(ctx, "The artist doesn't exist. Try again?")
        raise c_e.ExitFunction() from exc
