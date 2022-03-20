"""Contains stuff for forms."""


import nextcord as nx
import nextcord.ext.commands as cmds

import backend.utils.asking.wait_for as w_f
import backend.utils.views as vw
import backend.other_functions as o_f
import global_vars.variables as vrs

from ... import artist_structs as art
from .. import artist_info_bundle as bundle
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
    

    async def edit_loop(self, ctx: cmds.Context):
        """Edits the artist using dropdowns to select a section."""
        TIMEOUT = vrs.Timeouts.medium

        view_cls = f_s.FormSections.get_options_view("Select attribute to edit...")
        artist_info_bundle = bundle.InfoBundle(self.artist)

        while True:
            while True:
                new_view = view_cls()
                message_bundle = await artist_info_bundle.send_message(
                    ctx,
                    prefix = (
                        "This is the generated artist profile.\n"
                        "Select from the dropdown menu to edit that property.\n"
                        "Click on `Confirm` to finish editing the artist.\n"
                        "Click on `Cancel` to cancel the command.\n\n"
                        f"This command will timeout in `{o_f.format_time(TIMEOUT)}`."
                    ),
                    view = new_view
                )

                response_type = await w_f.wait_for_view(
                    ctx,
                    message_bundle.message_proof,
                    view = new_view,
                    timeout = TIMEOUT
                )

                response_type.value
