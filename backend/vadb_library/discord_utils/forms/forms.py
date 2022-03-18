"""Contains stuff for forms."""


import nextcord as nx
import nextcord.ext.commands as cmds

from ... import artist_structs as art


class ArtistAttrs():
    """Contains all `Artist` attributes for aski"""

class FormArtist():
    """Structure for editing the artist using a form on Discord."""
    def __init__(self, artist: art.Artist):
        self.artist = artist
