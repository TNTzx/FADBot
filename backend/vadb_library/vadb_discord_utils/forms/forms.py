"""Contains stuff for forms."""


import nextcord as nx

import backend.exc_utils as exc_utils
import backend.discord_utils as disc_utils
import backend.other as ot
import global_vars

from ... import artist_lib as art
from .. import artist_info_bundle as bundle
from . import form_exc as f_exc
from . import form_section_lib as f_s


class FormArtist():
    """Structure for editing the artist using a form on Discord."""
    def __init__(
            self,
            artist: art.Artist = art.Artist()
            ):
        self.artist = artist


    async def edit_with_section(self, channel: nx.TextChannel, author: nx.User, section: f_s.FormSection, section_state: f_s.SectionState = None):
        """Edits the artist on Discord with a form section."""
        try:
            await section.edit_artist_with_section(channel, author, self.artist, section_state = section_state)
        except f_exc.ExitSection:
            return


    async def edit_with_all_sections(self, channel: nx.TextChannel, author: nx.User, section_state: f_s.SectionState = None):
        """Edits the artist with all form sections."""
        for section in f_s.FormSections.get_all_form_sections():
            await self.edit_with_section(channel, author, section, section_state)


    async def edit_loop(self, channel: nx.TextChannel, author: nx.User):
        """Edits the artist using dropdowns to select a section."""
        timeout = global_vars.Timeouts.long

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
                    f"This command will timeout in {ot.format_time(timeout)}."
                )
            )

            return embed


        await channel.send("**Editing an artist...**")

        while True:
            while True:
                new_view = view_cls()
                message_bundle = await artist_info_bundle.send_message(
                    channel,
                    prefix = (
                        "This is the generated artist profile.\n"
                        "Select from the dropdown menu to edit that property.\n"
                        "Click on `Confirm` to finish editing the artist.\n"
                        "Click on `Cancel` to cancel the command.\n\n"
                        f"This command will timeout in `{ot.format_time(timeout)}`."
                    ),
                    view = new_view
                )

                response = await disc_utils.wait_for_view(
                    channel, author,
                    await message_bundle.message_pointer_proof.get_message(),
                    view = new_view,
                    timeout = timeout
                )


                if response.value == disc_utils.ViewOutputValues.CONFIRM:
                    break
                if response.value == disc_utils.ViewOutputValues.CANCEL:
                    await exc_utils.SendCancel(
                        error_place = exc_utils.ErrorPlace(channel, author)
                    ).send()

                title = response.value[0]
                await channel.send(f"Editing artist's __{title}__...")
                form_section = f_s.FormSections.get_section_from_title(title)

                await self.edit_with_section(channel, author, section = form_section, section_state = f_s.SectionStates.editing)


            view = disc_utils.ViewConfirmBackCancel()

            message = await channel.send(embed = generate_confirm_embed(), view = view)

            response = await disc_utils.wait_for_view(channel, author, message, view)

            if response.value == disc_utils.ViewOutputValues.CONFIRM:
                break
            if response.value == disc_utils.ViewOutputValues.BACK:
                continue
            if response.value == disc_utils.ViewOutputValues.CANCEL:
                await exc_utils.SendCancel(
                    error_place = exc_utils.ErrorPlace(channel, author)
                ).send()


        await channel.send("Artist edited successfully.")
