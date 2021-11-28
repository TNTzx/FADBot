"""Module that contains functions for waiting for responses."""

# pylint: disable=line-too-long
# pylint: disable=no-else-raise
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements

import asyncio
import requests as req
import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import functions.exceptions.custom_exc as c_e
import functions.exceptions.send_error as s_e
import functions.artist_related.is_using as i_u
import functions.other_functions as o_f


TIMEOUT = 60 * 10

async def send_error(ctx, suffix):
    """Sends an error, but with a syntax."""
    await s_e.send_error(ctx, f"{suffix} Try again.", send_author=True)

async def waiting(ctx: cmds.Context):
    """Wait for a message then return the response."""
    try:
        check = lambda msg: ctx.author.id == msg.author.id and isinstance(msg.channel, nx.channel.DMChannel)
        response: nx.Message = await vrs.global_bot.wait_for("message", check=check, timeout=TIMEOUT)
    except asyncio.TimeoutError as exc:
        await i_u.delete_is_using_command(ctx.author.id)
        await s_e.send_error(ctx, "Command timed out. Please use the command again.")
        raise c_e.ExitFunction("Exited Function.") from exc
    return response


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
            await send_error(ctx, "That's not a number!")
            return None
        return int(response.content)

    async def text():
        if await check_has_required(choices):
            if not response.content.lower() in [x.lower() for x in choices]:
                await send_error(ctx, "You didn't send a choice in the list of choices!")
                return None
            return response.content.lower()
        if response.content == "":
            await send_error(ctx, "You didn't send anything!")
            return None
        return response.content

    async def links():
        async def check_link(url):
            try:
                req.head(url)
            except req.exceptions.RequestException as exc:
                await send_error(ctx, f"You didn't send valid links! Here's the error:\n```{str(exc)}```")
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
                await send_error(ctx, f"You didn't send a valid image/link! Here's the error:\n```{str(exc)}```")
                return None

            if not image_request.headers["Content-Type"] in [f"image/{x}" for x in supported_formats]:
                await send_error(ctx, f"You sent a link to an unsupported file format! The formats allowed are `{'`, `'.join(supported_formats)}`.")
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
                await send_error(ctx, "Your formatting is wrong!")
                return None

            if not item[1].lower() in [x.lower() for x in choices_dict]:
                await send_error(ctx, f"Check if the right side of the colons contain these values: `{'`, `'.join(choices_dict)}`")
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

async def wait_for_response(ctx: cmds.Context,
        title, description, output_type,
        choices: list[str] = None, choices_dict: list[str] = None,
        skippable=False, skip_default=None):
    """Returns the response, but with checks."""

    success = True
    while success:
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

        await ctx.author.send(embed=embed)

        response = await waiting(ctx)

        if response.content == f"{vrs.CMD_PREFIX}cancel":
            raise c_e.ExitFunction("Exited Function.")
        elif response.content == f"{vrs.CMD_PREFIX}skip":
            if skippable:
                await ctx.author.send("Section skipped.")
                return skip_default
            else:
                await send_error(ctx, "You can't skip this section!")
                continue

        try:
            response = await reformat(ctx, output_type, response, choices=choices, choices_dict=choices_dict)
        except Exception as exc:
            await i_u.delete_is_using_command(ctx.author.id)
            raise exc
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
