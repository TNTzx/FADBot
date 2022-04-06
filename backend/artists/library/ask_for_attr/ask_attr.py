"""Module that contains functions for waiting for responses.
Used for setting artist objects attributes."""


import typing as typ
import requests as req
import nextcord as nx
import nextcord.ext.commands as nx_cmds

import global_vars.variables as vrs
import backend.other.asking.wait_for as w_f
import backend.other.views as vw
import backend.exc_utils.send_error as s_e
import backend.other_functions as o_f


TIMEOUT = vrs.Timeouts.long


async def check_has_required(choices):
    """Checks if there is a required choice."""
    if choices is not None:
        return len(choices) > 0
    return False
async def check_has_dict(choices, choices_dict):
    """Checks if there is a required choice for dicts.."""
    if choices is not None:
        return len(choices_dict) > 0
    return False


async def reformat(ctx: nx_cmds.Context, output_type: dict, response: nx.Message, choices_dict: list[str] = None,):
    """Reformats the response."""
    async def number():
        if not response.content.isnumeric():
            await w_f.send_error(ctx, "That's not a number!", send_author = True)
            return None
        return int(response.content)

    async def text():
        # if await check_has_required(choices):
        #     if not response.content.lower() in [x.lower() for x in choices]:
        #         await w_f.send_error(ctx, "You didn't send a choice in the list of choices!")
        #         return None
        #     return response.content.lower()
        if response.content == "":
            await w_f.send_error(ctx, "You didn't send anything!", send_author = True)
            return None
        return response.content

    async def links():
        async def check_link(url):
            try:
                req.head(url)
            except req.exceptions.RequestException as exc:
                await w_f.send_error(ctx, (
                    "You didn't send valid links! Here's the error:\n"
                    f"```{str(exc)}```"
                    ),
                    send_author = True
                )
                return None
            return url

        links = response.content.split("\n")
        for link in links:
            link = await check_link(link)
            if link is None:
                return None
        return links

    async def image():
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
                return None

            if not image_request.headers["Content-Type"] in [f"image/{x}" for x in supported_formats]:
                await w_f.send_error(ctx, f"You sent a link to an unsupported file format! The formats allowed are `{'`, `'.join(supported_formats)}`.", send_author = True)
                return None

            return image_url

        async def attachments():
            return await check_image(response.attachments[0].url)

        async def link():
            return await check_image(response.content)


        if not len(response.attachments) == 0:
            return await attachments()
        else:
            return await link()


    async def listing():
        return response.content.split("\n")

    async def dictionary():
        entries = response.content.split("\n")
        entry_dict = {}
        for entry in entries:
            item = entry.split(":")
            item = [x.lstrip(' ') for x in item]
            try:
                if not len(item) == 2:
                    raise IndexError()
                entry_dict[item[0]] = item[1].lower()
            except (KeyError, IndexError):
                await w_f.send_error(ctx, "Your formatting is wrong!", send_author = True)
                return None

            if not item[1].lower() in [x.lower() for x in choices_dict]:
                await w_f.send_error(ctx, f"Check if the right side of the colons contain these values: `{'`, `'.join(choices_dict)}`", send_author = True)
                return None
        return entry_dict

    if output_type == OutputTypes.number:
        return await number()
    elif output_type == OutputTypes.text:
        return await text()
    elif output_type == OutputTypes.links:
        return await links()
    elif output_type == OutputTypes.image:
        return await image()
    elif output_type == OutputTypes.listing:
        return await listing()
    elif output_type == OutputTypes.dictionary:
        return await dictionary()


async def ask_attribute(ctx: nx_cmds.Context,
        title, description, output_type,
        add_view: typ.Type[vw.View] = vw.Blank,
        choices_dict: list[str] = None,
        skippable = False, skip_default = None) -> str | int | list[str] | dict | vw.View:
    """Returns the response for setting attributes."""

    async def generate_embed():
        title_form = title if not skippable else f"{title} (skippable)"

        embed = nx.Embed(title = title_form, description = description, colour = 0xFFAEAE)

        def make_empty_field():
            embed.add_field(name = "_ _", value = "_ _", inline = False)

        make_empty_field()

        field_name = f"You have to send {output_type['prefix']} {output_type['type']}!"

        if not output_type == OutputTypes.choice:
            field_desc = (
                "__Here is an example of what you have to send:__\n"
                f"`{output_type['example']}`"
            )
        else:
            field_desc = "Choose from the dropdown menu!"

        embed.add_field(name = field_name, value = field_desc, inline = False)

        make_empty_field()

        skip_str = (
            f"This command times out in {o_f.format_time(TIMEOUT)}.\n" +
            ("Click on the \"Skip\" button to skip this section." if skippable else "") +
            "Click on the \"Cancel\" button to cancel the current command.\n"
        )
        embed.set_footer(text = skip_str)

        return embed

    class Merge(
            vw.ViewCancelSkip if skippable else vw.ViewCancelOnly,
            add_view):
        """Cancel Skip with custom view."""

    async def check_value(response: typ.Type[vw.View]):
        """Checks the value of a view."""
        if response.value == vw.OutputValues.cancel:
            await s_e.cancel_command(ctx, send_author = True)
        elif response.value == vw.OutputValues.skip:
            await ctx.author.send("Section skipped.")
            return skip_default
        return response


    while True:
        current_view = Merge()
        message = await ctx.author.send(
            embed = await generate_embed(),
            view = current_view
        )

        if not output_type == OutputTypes.choice:
            response_type, response = await w_f.wait_for_message_view(ctx, message, current_view, timeout = TIMEOUT)
            if response_type == w_f.OutputTypes.view:
                return await check_value(response)

            response = await reformat(ctx, output_type, response, choices_dict = choices_dict)
            if response is not None:
                break
        else:
            response = await w_f.wait_for_view(ctx, message, current_view, timeout = TIMEOUT)
            return await check_value(response)

    return response


class OutputTypes:
    """Available output types for the wait_for_response() function."""
    number = {
        "type": "number",
        "prefix": "a",
        "example": "1234531"
    }
    text = {
        "type": "text",
        "prefix": "some",
        "example": "This is a very cool string of text!"
    }
    choice = {
        "type": "choice",
        "prefix": "a",
        "example": "Click on the dropdown to select!"
    }
    links = {
        "type": "links",
        "prefix": "a list of",
        "example": (
            "https://www.youtube.com/FunnyArtistName\n"
            "https://open.spotify.com/AnotherFunnyArtistName"
        )
    }
    image = {
        "type": "image",
        "prefix": "an",
        "example": (
            "https://cdn.discordapp.com/attachments/888419023237316609/894910496199827536/beanss.jpg`\n"
            "`(OR you can upload your images as attachments like normal!)"
        )
    }
    listing = {
        "type": "list",
        "prefix": "a",
        "example": (
            "This is the first item on the list!\n"
            "This is the second item on the list!\n"
            "This is the third item on the list!"
        )
    }
    dictionary = {
        "type": "dictionary",
        "prefix": "a",
        "example": (
            "Remixes: Disallowed\n"
            "A very specific song: Verified"
        )
    }
