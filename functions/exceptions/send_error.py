"""Contains sending errors."""

# pylint: disable=line-too-long

import traceback
import nextcord as nx
import nextcord.ext.commands as commands

import global_vars.variables as vrs
import functions.other_functions as o_f


ERROR_PREFIX = "**Error!**\n"

async def send_error(ctx: commands.Context, suffix, exc="", other_data: nx.Message = None,
        send_author=False, send_owner=False, send_console=False, cooldown_reset=False):
    """Sends an error to a context."""

    bot: nx.Client = vrs.global_bot
    text = f"{ERROR_PREFIX}{ctx.author.mention}, {suffix}"
    tntz: nx.User = await o_f.get_tntz()

    if send_owner:
        extra = ""
        if not other_data is None:
            extra = f"\nOther Data: `{vars(other_data)}"

        await tntz.send(f"Error!\nCommand used: `{ctx.message.content}`{extra}\n```{exc}```")

    if send_console:
        error = getattr(exc, 'original', exc)
        print(f"Ignoring exception in command {ctx.command}:")
        # pylint: disable=no-member
        traceback.print_exception(type(error), error, error.__traceback__)
        # pylint: enable=no-member

    if cooldown_reset:
        ctx.command.reset_cooldown(ctx)

    if send_author:
        await ctx.author.send(text)
    else:
        if isinstance(ctx.message.channel, nx.DMChannel):
            channel = bot.get_channel(ctx.message.channel.id)
            await channel.send(text)
        else:
            await ctx.channel.send(text)
    return
