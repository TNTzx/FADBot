import discord
import main
import traceback
from Cogs import ErrorHandling

errorPrefix = ErrorHandling.errorPrefix
async def sendError(ctx, suffix, exc="", sendToOwner=False, printToConsole=False):
    await ctx.channel.send(f"{errorPrefix}{suffix}")
    
    if sendToOwner:
        tntz = await main.bot.fetch_user(279803094722674693)
        await tntz.send(f"Error in `{ctx.guild.name}`!\nLink: {ctx.message.jump_url}\n```{exc}```")
    if printToConsole:
        error = getattr(exc, 'original', exc)
        print(f"Ignoring exception in command {ctx.command}:")
        traceback.print_exception(type(error), error, error.__traceback__)
    return