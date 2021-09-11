import discord
import discord.ext.commands
import os
import asyncio

commandPrefix = "++"
bot = discord.Client()
bot = discord.ext.commands.Bot(command_prefix=commandPrefix)

apiLink = "https://fadb.live/"
apiCookie = {"access": os.environ['FadbAuthToken']}

def allCogs():
    return os.listdir(os.path.join(os.path.realpath(__file__), "..", "Cogs"))

for filename in allCogs():
    if filename.endswith(".py"):
        bot.load_extension(f"Cogs.{filename[:-3]}")

@bot.command()
async def restartswitch(ctx):
    await ctx.send("Restarting bot...")

    for filename in allCogs():
        if filename.endswith(".py"):
            newName = f"Cogs.{filename[:-3]}"
            bot.unload_extension(newName)
            bot.load_extension(newName)

    await ctx.send("Restarted!")

@bot.command()
async def killswitch(ctx):
    await ctx.send("Terminated.")
    await bot.logout()

botToken = os.environ['FadbToken']
bot.run(botToken)