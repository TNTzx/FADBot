"""Other fun functions!"""

import traceback
import datetime
import discord
import discord.ext.commands as commands

import main


ERROR_PREFIX = "**Error!**\n"


async def send_error(ctx: commands.Context, suffix, exc="", other_data: discord.Message = None,
        send_author=False, send_owner=False, send_console=False, cooldown_reset=False):
    """Sends an error to a context."""

    text = f"{ERROR_PREFIX}{ctx.author.mention}, {suffix}"
    tntz = await main.bot.fetch_user(279803094722674693)


    if send_owner:
        extra = ""
        if not other_data is None:
            extra = f"\nOther Data: `{vars(other_data)}"

        await tntz.send(f"Error!\nCommand used: `{ctx.message.content}`{extra}\n```{exc}```")

    if send_console:
        error = getattr(exc, 'original', exc)
        print(f"Ignoring exception in command {ctx.command}:")
        traceback.print_exception(type(error), error, error.__traceback__)

    if cooldown_reset:
        ctx.command.reset_cooldown(ctx)

    if send_author:
        await ctx.author.send(text)
    else:
        if isinstance(ctx.message.channel, discord.DMChannel):
            channel = main.bot.get_channel(ctx.message.channel.id)
            await channel.send(text)
        else:
            await ctx.channel.send(text)
    return


def format_time(num: int):
    """Formats the time from seconds to '#h #m #s'."""
    seconds = num
    time = str(datetime.timedelta(seconds=seconds))
    time = time.split(":")

    time_final_list = []
    if not time[0] == "0":
        time_final_list.append(f"{int(time[0])}h")
    if not time[1] == "00":
        time_final_list.append(f"{int(time[1])}m")
    if not time[2] == "00":
        time_final_list.append(f"{int(time[2])}s")

    time_final = " ".join(time_final_list)
    if time_final == "":
        time_final = "less than a second"
    return time_final


async def get_channel_from_mention(mention: str):
    """Gets channel from a mention."""
    get_id = mention[2:-1]
    obj = main.bot.get_channel(int(get_id))
    return obj
