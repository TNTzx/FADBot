"""Contains stuff for forms."""


import nextcord as nx
import nextcord.ext.commands as cmds

import backend.exceptions.send_error as s_e
import backend.utils.asking.wait_for as w_f
import backend.utils.views as vw
import backend.other_functions as o_f
import global_vars.variables as vrs

from ... import artists as art
from .. import artist_info_bundle as bundle
from . import form_exc as f_exc
from . import form_sections as f_s


class FormArtist():
    """Structure for editing the artist using a form on Discord."""
    def __init__(self, artist: art.Artist):
        self.artist = artist


    async def edit_with_section(self, ctx: cmds.Context, section: f_s.FormSection, section_state: f_s.SectionState = None):
        """Edits the artist on Discord with a form section."""
        try:
            await section.edit_artist_with_section(ctx, self.artist, section_state = section_state)
        except f_exc.ExitSection:
            return


    async def edit_with_all_sections(self, ctx: cmds.Context, section_state: f_s.SectionState = None):
        """Edits the artist with all form sections."""
        for section in f_s.FormSections.get_all_form_sections():
            await self.edit_with_section(ctx, section, section_state)


    async def edit_loop(self, ctx: cmds.Context):
        """Edits the artist using dropdowns to select a section."""
        timeout = vrs.Timeouts.long

        view_cls = f_s.FormSections.get_options_view("Select attribute to edit...")
        artist_info_bundle = bundle.InfoBundle(self.artist)

        def generate_confirm_embed():
            embed = nx.Embed(
                title = "Confirm editing artist",
                description = (
                    "Are you sure that the entered information for this artist is correct?"
                )
            )

            embed.set_footer(
                text = (
                    "Click on \"Confirm\" to confirm that you have finished editing the artist.\n"
                    "Click on \"Back\" to go back and resume editing the artist.\n"
                    "Click on \"Cancel\" to cancel the current command.\n\n"
                    f"This command will timeout in {o_f.format_time(timeout)}."
                )
            )

            return embed


        await ctx.author.send("**Editing an artist...**")

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
                        f"This command will timeout in `{o_f.format_time(timeout)}`."
                    ),
                    view = new_view
                )

                response = await w_f.wait_for_view(
                    ctx,
                    message_bundle.message_pointer_proof,
                    view = new_view,
                    timeout = timeout
                )


                if response.value == vw.OutputValues.confirm:
                    break
                if response.value == vw.OutputValues.cancel:
                    await s_e.cancel_command(ctx, send_author = True)

                title = response.value[0]
                await ctx.author.send(f"Editing artist's __{title}__...")
                form_section = f_s.FormSections.get_section_from_title(title)

                await self.edit_with_section(ctx, section = form_section, section_state = f_s.SectionStates.editing)


            view = vw.ViewConfirmBackCancel()

            message = await ctx.send(embed = generate_confirm_embed(), view = view)

            response = await w_f.wait_for_view(ctx, message, view)

            if response.value == vw.OutputValues.confirm:
                break
            if response.value == vw.OutputValues.back:
                continue
            if response.value == vw.OutputValues.cancel:
                await s_e.cancel_command(ctx, send_author = True)


        await ctx.author.send("Artist edited successfully.")
