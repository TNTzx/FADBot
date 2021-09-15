import discord
import main
import traceback
from Cogs import ErrorHandling
import datetime

errorPrefix = ErrorHandling.errorPrefix
async def sendError(ctx, suffix, exc="", sendToAuthor=False, sendToOwner=False, printToConsole=False):
    text = f"{errorPrefix}{ctx.author.mention}, {suffix}"
    
    if sendToOwner:
        tntz = await main.bot.fetch_user(279803094722674693)
        await tntz.send(f"Error in `{ctx.guild.name}`!\nLink: {ctx.message.jump_url}\n```{exc}```")
    if printToConsole:
        error = getattr(exc, 'original', exc)
        print(f"Ignoring exception in command {ctx.command}:")
        traceback.print_exception(type(error), error, error.__traceback__)
    if sendToAuthor:
        await ctx.author.send(text)
    else:
        await ctx.channel.send(text)
    return

async def subtractList(list1, list2):
    return [x for x in list1 if x not in list2]

async def formatTime(num):
    numberOfSeconds = num
    timeConverted = str(datetime.timedelta(seconds=numberOfSeconds))
    timeSplit = timeConverted.split(":")

    timeFinalList = []
    if not timeSplit[0] == "0":
        timeFinalList.append(f"{int(timeSplit[0])}h")
    if not timeSplit[1] == "00":
        timeFinalList.append(f"{int(timeSplit[1])}m")
    if not timeSplit[2] == "00":
        timeFinalList.append(f"{int(timeSplit[2])}s")

    timeFinal = ", ".join(timeFinalList)
    return timeFinal

