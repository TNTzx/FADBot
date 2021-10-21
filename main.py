"""Where the bot starts its life."""

import os
import discord
import discord.ext.commands as cmds


CMD_PREFIX = "##"
bot = discord.Client()

intents = discord.Intents.default()
intents.members = True

bot = cmds.Bot(command_prefix=CMD_PREFIX, intents=intents)
bot.remove_command("help")


# Load all cogs
print("Loading cogs...")
def all_cogs():
    """Returns all cogs."""
    return os.listdir(os.path.join(os.path.dirname(__file__), ".", "Cogs"))

for filename in all_cogs():
    if filename.endswith(".py"):
        if filename == "__init__.py":
            continue
        print(f"Loading cog '{filename}'...")
        bot.load_extension(f"Cogs.{filename[:-3]}")

print("Loaded all cogs!")


# Important commands
def restart_bot():
    """Restarts the bot by reloading all cogs."""
    for file in all_cogs():
        if file.endswith(".py"):
            if file == "__init__.py":
                continue
            new_file = f"Cogs.{file[:-3]}"

            try:
                bot.unload_extension(new_file)
            except cmds.errors.ExtensionNotLoaded:
                continue
            bot.load_extension(new_file)

def test_for_commands(command):
    """Prints the commands registered."""
    print(bot.all_commands.keys(), command in bot.all_commands.keys())

# testForCommands("test")

# Log in
print("Logging into bot...")
bot_token = os.environ['FadbToken']
bot.run(bot_token)
