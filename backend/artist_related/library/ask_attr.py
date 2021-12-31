"""Module that contains functions for waiting for responses.
Used for setting artist objects attributes."""

# pylint: disable=line-too-long
# pylint: disable=no-else-raise
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=unused-argument

import requests as req
import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import backend.main_library.asking.wait_for as w_f
import backend.exceptions.custom_exc as c_e
import backend.other_functions as o_f


TIMEOUT = 60 * 10


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


async def reformat(ctx: cmds.Context, output_type: dict, response: nx.Message, choices: list[str] = None, choices_dict: list[str] = None,):
    """Reformats the response."""
    async def number():
        if not response.content.isnumeric():
            await w_f.send_error(ctx, "That's not a number!")
            return None
        return int(response.content)

    async def text():
        if await check_has_required(choices):
            if not response.content.lower() in [x.lower() for x in choices]:
                await w_f.send_error(ctx, "You didn't send a choice in the list of choices!")
                return None
            return response.content.lower()
        if response.content == "":
            await w_f.send_error(ctx, "You didn't send anything!")
            return None
        return response.content

    async def links():
        async def check_link(url):
            try:
                req.head(url)
            except req.exceptions.RequestException as exc:
                await w_f.send_error(ctx, f"You didn't send valid links! Here's the error:\n```{str(exc)}```")
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
                await w_f.send_error(ctx, f"You didn't send a valid image/link! Here's the error:\n```{str(exc)}```")
                return None

            if not image_request.headers["Content-Type"] in [f"image/{x}" for x in supported_formats]:
                await w_f.send_error(ctx, f"You sent a link to an unsupported file format! The formats allowed are `{'`, `'.join(supported_formats)}`.")
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
                    raise IndexError

                if not await check_has_dict(choices, choices_dict):
                    entry_dict[item[0]] = item[1]
                else:
                    entry_dict[item[0]] = item[1].lower()
            except (KeyError, IndexError):
                await w_f.send_error(ctx, "Your formatting is wrong!")
                return None

            if not item[1].lower() in [x.lower() for x in choices_dict]:
                await w_f.send_error(ctx, f"Check if the right side of the colons contain these values: `{'`, `'.join(choices_dict)}`")
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


class Cancel(nx.ui.View):
    """An example view."""
    def __init__(self):
        super().__init__()
        self.value = None

    @nx.ui.button(label="one", style=nx.ButtonStyle.green)
    async def button_one(self, button: nx.ui.Button, interact: nx.Interaction):
        """Button!"""
        self.value = "one"
        self.stop()

async def ask_attribute(ctx: cmds.Context,
        title, description, output_type,
        choices: list[str] = None, choices_dict: list[str] = None,
        skippable=False, skip_default=None):
    """Returns the response, but with checks."""

    success = True
    while success:
        async def generate_embed():
            title_form = title if not skippable else f"{title} (skippable)"

            embed = nx.Embed(title=title_form, description=description, colour=0xFFAEAE)
            embed.add_field(name="_ _", value="_ _", inline=False)

            field_name = f"You have to send {output_type['prefix']} {output_type['type']}!"

            if not await check_has_required(choices):
                field_desc = f"__Here is an example of what you have to send:__\n`{output_type['example']}`"
                embed.add_field(name=field_name, value=field_desc, inline=False)
            else:
                field_desc = f"Choose from one of the following choices: \n`{'`, `'.join(choices)}`"
                embed.add_field(name=field_name, value=field_desc, inline=False)

            embed.add_field(name="_ _", value="_ _", inline=False)

            skip_str = f"This command times out in {o_f.format_time(TIMEOUT)}. \nUse {vrs.CMD_PREFIX}cancel to cancel the current command." + (f"\nUse {vrs.CMD_PREFIX}skip to skip this section." if skippable else "")
            embed.set_footer(text=skip_str)

            return embed

        await ctx.author.send(embed=await generate_embed())

        response = await w_f.wait_for_response(ctx)

        if response.content == f"{vrs.CMD_PREFIX}cancel":
            await ctx.author.send("Command cancelled.")
            raise c_e.ExitFunction("Exited Function.")
        elif response.content == f"{vrs.CMD_PREFIX}skip":
            if skippable:
                await ctx.author.send("Section skipped.")
                return skip_default
            await w_f.send_error(ctx, "You can't skip this section!")
            continue

        response = await reformat(ctx, output_type, response, choices=choices, choices_dict=choices_dict)
        success = (response is None)
    return response

class OutputTypes:
    """Available output types for the wait_for_response() function."""
    number = {"type": "number",
        "prefix": "a",
        "example": "1234531"}
    text = {"type": "text",
        "prefix": "some",
        "example": "This is a very cool string of text!"}
    links = {"type": "links",
        "prefix": "a list of",
        "example": "https://www.youtube.com/FunnyArtistName\nhttps://open.spotify.com/AnotherFunnyArtistName"}
    image = {"type": "image",
        "prefix": "an",
        "example": "https://cdn.discordapp.com/attachments/888419023237316609/894910496199827536/beanss.jpg`\n`(OR you can upload your images as attachments like normal!)"}
    listing = {"type": "list",
        "prefix": "a", "example":
        "This is the first item on the list!\nThis is the second item on the list!\nThis is the third item on the list!"}
    dictionary = {"type": "dictionary",
        "prefix": "a",
        "example": "Remixes: Disallowed\nA very specific song: Verified"}
