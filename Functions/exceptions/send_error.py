"""Contains sending errors."""

import traceback
import discord
import discord.ext.commands as commands


ERROR_PREFIX = "**Error!**\n"

async def send_error(ctx: commands.Context, bot: discord.Client, suffix, exc="", other_data: discord.Message = None,
        send_author=False, send_owner=False, send_console=False, cooldown_reset=False):
    """Sends an error to a context."""

    text = f"{ERROR_PREFIX}{ctx.author.mention}, {suffix}"
    tntz = await bot.fetch_user(279803094722674693)


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
            channel = bot.get_channel(ctx.message.channel.id)
            await channel.send(text)
        else:
            await ctx.channel.send(text)
    return
