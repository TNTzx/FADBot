"""Contains stuff for forms."""


import nextcord as nx
import nextcord.ext.commands as cmds

from ... import artist_structs as art
from . import form_sections as f_s


class FormArtist():
    """Structure for editing the artist using a form on Discord."""
    def __init__(self, artist: art.Artist):
        self.artist = artist


    async def edit_with_section(self, ctx: cmds.Context, section: f_s.FormSection, section_state: f_s.SectionState = None):
        """Edits the artist on Discord with a form section."""
        try:
            await section.edit_artist_with_section(ctx, self.artist, section_state = section_state)
        except f_s.ExitSection:
            return
