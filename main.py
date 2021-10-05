import discord
import discord.ext.commands as commands
import json
import pyrebase
import os
import asyncio


commandPrefix = "##"
bot = discord.Client()
bot = commands.Bot(command_prefix=commandPrefix)
bot.remove_command("help")

# Load all cogs
print("Loading cogs...")
def allCogs():
    return os.listdir(os.path.join(os.path.dirname(__file__), ".", "Cogs"))

for filename in allCogs():
    if filename.endswith(".py"):
        print(f"Loading cog '{filename}'...")
        bot.load_extension(f"Cogs.{filename[:-3]}")

print("Loaded all cogs!")


# Important commands
print("Loading important commands...")

def restartBot():
    for filename in allCogs():
            if filename.endswith(".py"):
                newName = f"Cogs.{filename[:-3]}"
                try:
                    bot.unload_extension(newName)
                except commands.errors.ExtensionNotLoaded:
                    continue
                bot.load_extension(newName)

print("Loaded all important commands!")

# Log in
print("Logging into bot...")
botToken = os.environ['FadbToken']
bot.run(botToken)