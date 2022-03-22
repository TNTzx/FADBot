""""Contains logic for form sections."""


from __future__ import annotations

import typing as typ

import requests as req

import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import backend.utils.views as vw
import backend.utils.asking.wait_for as w_f
import backend.exceptions.send_error as s_e
import backend.other_functions as o_f

from .... import artists as a_s
from .. import form_exc as f_exc
from . import section_states as states


async def check_response(ctx: cmds.Context, view: vw.View):
    """Checks the response of the user if they went back, cancelled, etc."""
    if view.value == vw.OutputValues.cancel:
        await s_e.cancel_command(ctx, send_author=True)
    elif view.value == vw.OutputValues.skip:
        await ctx.author.send("Section skipped.")
        raise f_exc.ExitSection()
    elif view.value == vw.OutputValues.back:
        await ctx.author.send("Going back to menu...")
        raise f_exc.ExitSection()


class FormSection():
    """A form section."""
    form_sections: list[FormSection] = []


    text_ext: str = None
    timeout: int = vrs.Timeouts.long
    instructions: str = None

    def __init__(
            self,
            title: str,
            description: str,
            example: str = None,
            notes: str = None,
            default_section_state: states.SectionState = states.SectionStates.default
            ):
        self.title = title
        self.description = description
        self.example = example
        self.notes = notes
        self.default_section_state = default_section_state

        self.__class__.form_sections.append(self)


    def generate_embed(self, section_state: states.SectionState = None, timeout: int = None):
        """Generates the embed for this section."""
        if timeout is None:
            timeout = self.timeout
        if section_state is None:
            section_state = self.default_section_state

        emb_title = f"Current Section: {self.title.title()}"

        if section_state != states.SectionStates.default:
            emb_title = f"{emb_title} ({section_state.name})"

        embed = nx.Embed(color = vrs.COLOR_PA, title = emb_title)


        embed.add_field(name = "**Description:**", value = self.description, inline = False)


        embed.add_field(
            name = f"You have to send {self.text_ext}!",
            value = f"**Instructions:**\n{self.instructions}",
            inline = False
        )

        if self.example is not None:
            embed.add_field(
                name = "Example:",
                value = f"`{self.example}`",
                inline = False
            )
        if self.notes is not None:
            embed.add_field(
                name = "Notes:",
                value = self.notes,
                inline = False
            )


        emb_footer_extra = f"This command times out in {o_f.format_time(timeout)}."
        embed.set_footer(text = f"{section_state.footer}\n\n{emb_footer_extra}")

        return embed


    def generate_option(self):
        """Generates a `ChoiceOption` object for this form section."""
        return nx.SelectOption(
            label = self.title.capitalize(),
            description = self.description,
            value = self.title
        )


    async def reformat_input(
            self,
            ctx: cmds.Context,
            response: nx.Message | vw.View,
            section_state: states.SectionState = None
            ) -> str | int | dict | list | vw.View:
        """Validates the input."""
        raise f_exc.InvalidSectionResponse()


    # TODO try to make this be able to send anywhere, not just author
    async def send_section(
            self,
            ctx: cmds.Context,
            section_state: states.SectionState = None,
            extra_view: typ.Type[vw.View] = vw.Blank,
            timeout: int = None
            ):
        """Sends the section to the user then returns the output."""
        if timeout is None:
            timeout = self.timeout
        if section_state is None:
            section_state = self.default_section_state

        class ViewMerged(section_state.view_cls, extra_view):
            """Merged views."""

        while True:
            current_view = ViewMerged()
            message = await ctx.author.send(
                embed = self.generate_embed(
                    section_state = section_state,
                    timeout = timeout
                ),
                view = current_view
            )

            response_type, response = await w_f.wait_for_message_view(ctx, message, current_view, timeout = timeout)

            if response_type == w_f.OutputTypes.view:
                await check_response(ctx, response)

            try:
                final_response = await self.reformat_input(ctx, response, section_state)
            except f_exc.InvalidSectionResponse:
                continue
            except f_exc.ExitSection:
                pass

            await ctx.author.send(f"**Artist's {self.title} is now set.**")
            return final_response


    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        """Edits the artist with the section."""



class ViewInput(FormSection):
    """A `FormSection` with a view input."""

class TextInput(FormSection):
    """A `FormSection` with a text input."""


async def check_if_content_empty(ctx: cmds.Context, response: nx.Message):
    """Checks if the response is empty, as if sending an attachment with no message. If it is empty, raise InvalidSectionResponse."""
    if response.content == "":
        await w_f.send_error(ctx, "You didn't send anything!", send_author = True)
        raise f_exc.InvalidSectionResponse("No message content found.")


class NumberSection(TextInput):
    """A number section."""
    text_ext = "a number"
    instructions = "Send a number!"

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View, section_state: states.SectionState = None):
        await check_if_content_empty(ctx, response)

        try:
            number = int(response.content)
        except ValueError as exc:
            await w_f.send_error(ctx, "That's not a number!", send_author = True)
            raise f_exc.InvalidSectionResponse() from exc

        if number > (1 * (10 ** 6)):
            await w_f.send_error(ctx, "That's way too large!", send_author = True)
            raise f_exc.InvalidSectionResponse()


        return number


class RawTextSection(TextInput):
    """A text section."""
    text_ext = "some text"
    instructions = "Send any plain text!"

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View, section_state: states.SectionState = None):
        await check_if_content_empty(ctx, response)

        return response.content


class LinksSection(TextInput):
    """A links section."""
    text_ext = "some links"
    instructions = (
        "Send a link!\n"
        "You can also send more than one link by separating each link with a newline (using `CTRL + Enter` on PC, or just `Enter` on mobile)."
    )

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View, section_state: states.SectionState = None):
        await check_if_content_empty(ctx, response)

        async def check_link(url):
            try:
                req.head(url)
            except req.exceptions.RequestException as exc:
                await w_f.send_error(ctx, (
                    f"`{url}` is not a valid link! Here's the error:\n"
                    f"```{str(exc)}```"
                    ),
                    send_author = True
                )
                raise f_exc.InvalidSectionResponse() from exc
            return url

        links = response.content.split("\n")
        for link in links:
            link = await check_link(link)
        return links


class ImageSection(TextInput):
    """An image section."""
    text_ext = "an image / image url"
    instructions = (
        "Send an image!\n"
        "You can send an image using an attachment (uploading the file directly to Discord) or using a direct URL link of the image!"
    )

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View, section_state: states.SectionState = None):
        async def check_image(image_url):
            supported_formats = ["png", "jpg", "jpeg"]

            try:
                image_request = req.head(image_url)
            except req.exceptions.RequestException as exc:
                await w_f.send_error(ctx, (
                    f"You didn't send a valid image/link! Here's the error:\n"
                    f"```{str(exc)}```"
                    ),
                    send_author = True
                )
                raise f_exc.InvalidSectionResponse() from exc

            if not image_request.headers["Content-Type"] in [f"image/{x}" for x in supported_formats]:
                await w_f.send_error(ctx, f"You sent a link to an unsupported file format! The formats allowed are `{'`, `'.join(supported_formats)}`.", send_author = True)
                raise f_exc.InvalidSectionResponse()

            return image_url


        if not len(response.attachments) == 0:
            return await check_image(response.attachments[0].url)

        return await check_image(response.content)


class ListSection(TextInput):
    """A list section."""
    text_ext = "a list"
    instructions = (
        "Send a list!\n"
        "Separate each item in the list with a newline (using `CTRL + Enter` on PC, or just `Enter` on mobile)."
    )

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View, section_state: states.SectionState = None):
        await check_if_content_empty(ctx, response)

        if response.content == "":
            await w_f.send_error(ctx, "You didn't send a list!", send_author = True)
            raise f_exc.InvalidSectionResponse()
        return response.content.split("\n")


class DictSection(TextInput):
    """A dictionary section."""
    text_ext = "a dictionary"
    instructions = (
        "Send a dictionary!\n"
        "A dictionary pairs a certain value to another value, like how a real dictionary book pairs a word with its definition.\n"
        "The value on the left of the colon (`:`) is the *key*, and the value on the right of the colon is its *value*."
        "Separate each item in the dictionary with a newline (using `CTRL + Enter` on PC, or just `Enter` on mobile)."
    )

    def __init__(
            self, title: str, description: str, example: str = None, notes: str = None,
            default_section_state: states.SectionState = states.SectionStates.default,
            allowed_key_func: typ.Callable[[typ.Any], bool] = None, allowed_val_func: typ.Callable[[typ.Any], bool] = None
            ):
        super().__init__(title, description, example, notes, default_section_state = default_section_state)
        self.allowed_key_func = allowed_key_func
        self.allowed_val_func = allowed_val_func

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View, section_state: states.SectionState = None):
        await check_if_content_empty(ctx, response)

        diction = {}
        try:
            entry = response.content.split("\n")
            for item in entry:
                key_value = item.split(":")
                key_value = [x.lstrip(' ') for x in key_value]
                diction[key_value[0]] = key_value[1]
        except (ValueError, IndexError) as exc:
            await w_f.send_error(ctx, "Your formatting is wrong!", send_author = True)
            raise f_exc.InvalidSectionResponse() from exc


        async def check(type_: str, func: typ.Callable[[typ.Any], bool] | None, dict_view: list):
            if func is not None:
                for item in dict_view:
                    if not func(item):
                        await w_f.send_error(ctx, f"`{item}` is not a valid {type_}. Please check if you have capitalized it.", send_author = True)
                        raise f_exc.InvalidSectionResponse()

        await check("key", self.allowed_key_func, list(diction.keys()))
        await check("value", self.allowed_val_func, list(diction.values()))

        return diction


class ChoiceSection(ViewInput):
    """A choice section."""
    text_ext = "a choice"
    instructions = "Select an item in the choices below!"

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View, section_state: states.SectionState = None):
        if isinstance(response, nx.Message):
            await w_f.send_error(ctx, "You didn't send a choice!", send_author = True)
            raise f_exc.InvalidSectionResponse()

        return response.value[0]
