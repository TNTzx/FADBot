""""Contains logic for form sections."""


from __future__ import annotations

import typing as typ

import requests as req

import nextcord as nx
import nextcord.ext.commands as cmds

import backend.utils.views as vw
import backend.utils.asking.wait_for as w_f
import backend.exceptions.send_error as s_e
import global_vars.variables as vrs

from .... import artist_structs as a_s
from . import section_states as states


class InvalidResponse(Exception):
    """Invalid Response."""

class ExitSection(Exception):
    """Section exited."""


async def check_response(ctx: cmds.Context, view: vw.View):
    """Checks the response of the user if they went back, cancelled, etc."""
    if view.value == vw.OutputValues.cancel:
        await s_e.cancel_command(ctx, send_author=True)
    elif view.value == vw.OutputValues.skip:
        await ctx.author.send("Section skipped.")
        raise ExitSection()
    elif view.value == vw.OutputValues.back:
        await ctx.author.send("Going back to menu...")
        raise ExitSection()
    else:
        raise NotImplementedError("Not implemented response.")


class FormSection():
    """A form section."""
    form_sections: list[FormSection] = []


    text_ext: str = None

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


    def generate_embed(self, section_state: states.SectionState = None):
        """Generates the embed for this section."""
        if section_state is None:
            section_state = self.default_section_state

        def make_empty_field(embed: nx.Embed):
            """Makes an empty field on the embed."""
            embed.add_field(name="_ _", value="_ _", inline=False)

        if section_state == states.SectionStates.default:
            emb_title = self.title.capitalize()
        else:
            emb_title = f"{self.title.capitalize()} ({section_state.name})"

        embed = nx.Embed(color = vrs.COLOR_PA, title = emb_title)

        make_empty_field(embed)

        embed.add_field(name = "**Description:**", value = self.description, inline = False)


        emb_req = f"You have to send {self.text_ext}!"

        emb_req_desc = []
        if self.example is not None:
            emb_req_desc.append((
                "__Examples:__\n"
                f"`{self.example}`"
            ))
        if self.notes is not None:
            emb_req_desc.append(f"__Note:__\n{self.notes}")

        embed.add_field(name = emb_req, value = "\n".join(emb_req_desc), inline = False)

        make_empty_field(embed)

        embed.set_footer(text = section_state.footer)

        return embed


    def generate_option(self):
        """Generates a `ChoiceOption` object for this form section."""
        return nx.SelectOption(
            label = self.title.capitalize(),
            value = self.description
        )


    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View):
        """Validates the input."""
        raise InvalidResponse()


    async def send_section(self, ctx: cmds.Context, section_state: states.SectionState = None, extra_view: typ.Type[vw.View] = vw.Blank):
        """Sends the section to the user then returns the output."""
        if section_state is None:
            section_state = self.default_section_state

        class ViewMerged(section_state.view_cls, extra_view):
            """Merged views."""

        while True:
            current_view = ViewMerged()
            message = await ctx.author.send(
                embed = self.generate_embed(section_state),
                view = current_view
            )

            response_type, response = await w_f.wait_for_message_view(ctx, message, current_view, timeout = vrs.Timeouts.long)

            if response_type == w_f.OutputTypes.view:
                await check_response(ctx, response)

                return response
            if response_type == w_f.OutputTypes.message:
                try:
                    return await self.reformat_input(ctx, response)
                except InvalidResponse:
                    continue


    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        """Edits the artist with the section."""



class ViewInput(FormSection):
    """A `FormSection` with a view input."""

class TextInput(FormSection):
    """A `FormSection` with a text input."""


class NumberSection(TextInput):
    """A number section."""
    text_ext = "a number"

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View):
        if not response.content.isnumeric():
            await w_f.send_error(ctx, "That's not a number!")
            return None
        return int(response.content)


class RawTextSection(TextInput):
    """A text section."""
    text_ext = "some text"

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View):
        if response.content == "":
            await w_f.send_error(ctx, "You didn't send text!")
            raise InvalidResponse()
        return response.content


class LinksSection(TextInput):
    """A links section."""
    text_ext = "some links"

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View):
        async def check_link(url):
            try:
                req.head(url)
            except req.exceptions.RequestException as exc:
                await w_f.send_error(ctx, (
                    f"`{url}` is not a valid link! Here's the error:\n"
                    f"```{str(exc)}```"
                ))
                raise InvalidResponse() from exc
            return url

        links = response.content.split("\n")
        for link in links:
            link = await check_link(link)
        return links

class ImageSection(TextInput):
    """An image section."""
    text_ext = "an image / image url"

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View):
        async def check_image(image_url):
            supported_formats = ["png", "jpg", "jpeg"]

            try:
                image_request = req.head(image_url)
            except req.exceptions.RequestException as exc:
                await w_f.send_error(ctx, (
                    f"You didn't send a valid image/link! Here's the error:\n"
                    f"```{str(exc)}```"
                ))
                return None

            if not image_request.headers["Content-Type"] in [f"image/{x}" for x in supported_formats]:
                await w_f.send_error(ctx, f"You sent a link to an unsupported file format! The formats allowed are `{'`, `'.join(supported_formats)}`.")
                return None

            return image_url


        if not len(response.attachments) == 0:
            return await check_image(response.attachments[0].url)

        return await check_image(response.content)


class ListSection(TextInput):
    """A list section."""
    text_ext = "a list"

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View):
        return response.content.split("\n")


class DictSection(TextInput):
    """A dictionary section."""
    text_ext = "a dictionary"

    def __init__(
            self, title: str, description: str, example: str = None, notes: str = None,
            default_section_state: states.SectionState = states.SectionStates.default,
            allowed_key_func: typ.Callable[[typ.Any], bool] = None, allowed_val_func: typ.Callable[[typ.Any], bool] = None
            ):
        super().__init__(title, description, example, notes, default_section_state = default_section_state)
        self.allowed_key_func = allowed_key_func
        self.allowed_val_func = allowed_val_func

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View):
        diction = {}
        try:
            entry = response.content.split("\n")
            for item in entry:
                key_value = item.split(":")
                key_value = [x.lstrip(' ') for x in key_value]
                diction[key_value[0]] = key_value[1]
        except (ValueError, IndexError) as exc:
            await w_f.send_error(ctx, "Your formatting is wrong!")
            raise InvalidResponse() from exc


        async def check(type_: str, func: typ.Callable[[typ.Any], bool] | None, dict_view: list):
            if func is not None:
                for item in dict_view:
                    if not func(item):
                        await w_f.send_error(ctx, f"`{item}` is not a valid {type_}.")
                        raise InvalidResponse()

        await check("key", self.allowed_key_func, list(diction.keys()))
        await check("value", self.allowed_val_func, list(diction.values()))

        return diction


class ChoiceSection(ViewInput):
    """A choice section."""
    text_ext = "a choice"

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View):
        new_response = response.value[0]
