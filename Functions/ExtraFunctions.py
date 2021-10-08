import discord
import discord.ext.commands as commands
import main
import traceback

import datetime

otherData = ""
errorPrefix = "**Error!**\n"

async def sendError(ctx:commands.Context, suffix, exc="", sendToAuthor=False, sendToOwner=False, printToConsole=False, resetCooldown=False):
    text = f"{errorPrefix}{ctx.author.mention}, {suffix}"
    tntz = await main.bot.fetch_user(279803094722674693)
    
    if sendToOwner:
        extra = f", Other Data: `{otherData}`" if len(otherData) > 0 else ""
        await tntz.send(f"Error in `{ctx.guild.name}`!\nLink: {ctx.message.jump_url}\nCommand used: `{ctx.message.content}`{extra} `\n```{exc}```")

    if printToConsole:
        error = getattr(exc, 'original', exc)
        print(f"Ignoring exception in command {ctx.command}:")
        traceback.print_exception(type(error), error, error.__traceback__)
    
    if resetCooldown:
        ctx.command.reset_cooldown(ctx) 

    if sendToAuthor:
        await ctx.author.send(text)
    else:
        if isinstance(ctx.message.channel, discord.DMChannel):
            channel = main.bot.get_channel(ctx.message.channel.id)
            await channel.send(text)
        else:
            await ctx.channel.send(text)
    return


async def subtractList(list1, list2):
    return [x for x in list1 if x not in list2]


def formatTime(num):
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

    timeFinal = " ".join(timeFinalList)
    if timeFinal == "":
        timeFinal = "less than a second"
    return timeFinal

async def getChannelFromMention(mention):
    channelId = mention[2:-1]
    channelObj = main.bot.get_channel(int(channelId))
    return channelObj
