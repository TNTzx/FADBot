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

adminRole = "///Moderator"

apiLink = "https://fadb.live/"
apiAuthToken = os.environ["FadbAuthToken"]
apiHeaders = {
  "Authorization": f"Basic {apiAuthToken}",
  "Content-Type": "application/x-www-form-urlencoded"
}

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

@bot.command(aliases=["sr"])
@commands.guild_only()
@commands.has_role(adminRole)
async def switchrestart(ctx):
    await ctx.send("Restarting bot...")

    for filename in allCogs():
        if filename.endswith(".py"):
            newName = f"Cogs.{filename[:-3]}"
            try:
                bot.unload_extension(newName)
            except commands.errors.ExtensionNotLoaded:
                continue
            bot.load_extension(newName)

    await ctx.send("Restarted!")
    print("\n \n Restart break! -------------------------------------- \n \n")

@bot.command(aliases=["sk"])
@commands.guild_only()
@commands.has_role(adminRole)
async def switchkill(ctx):
    await ctx.send("Terminated bot.")
    await bot.logout()

print("Loaded all important commands!")

# Log in
print("Logging into bot...")
botToken = os.environ['FadbToken']
bot.run(botToken)