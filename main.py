import discord
from discord.ext import commands
# import discord_slash.utils.manage_commands as dsumc
# import discord_slash.model as dsm
import discord.ext.commands
import discord_slash
import os
import asyncio


commandPrefix = "##"

intents = discord.Intents.all()
bot = discord.Client()
bot = discord.ext.commands.Bot(command_prefix=commandPrefix)
slash = discord_slash.SlashCommand(bot, sync_commands=True)

# guildIds = [734204348665692181]
adminRole = "beans"
verifyEmote = "\u2705"

apiLink = "https://fadb.live/"
apiAuthToken = os.environ["FadbAuthToken"]
apiHeaders = {
  "Authorization": f"Basic {apiAuthToken}",
  "Content-Type": "application/x-www-form-urlencoded"
}

#Cogs
def allCogs():
    return os.listdir(os.path.join(os.path.realpath(__file__), "..", "Cogs"))

for filename in allCogs():
    if filename.endswith(".py"):
        bot.load_extension(f"Cogs.{filename[:-3]}")


@bot.command()
@commands.has_role(adminRole)
async def restartswitch(ctx):
    await ctx.send("Restarting bot...")

    for filename in allCogs():
        if filename.endswith(".py"):
            newName = f"Cogs.{filename[:-3]}"
            try:
                bot.unload_extension(newName)
            finally:
                bot.load_extension(newName)

    await ctx.send("Restarted!")

@bot.command()
@commands.has_role(adminRole)
async def killswitch(ctx):
    await ctx.send("Terminated.")
    await bot.logout()

botToken = os.environ["FadbToken"]
bot.run(botToken)