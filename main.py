"""Where the bot starts its life."""

# pylint: disable=assigning-non-slot

import os
import discord
import discord.ext.commands as cmds

from global_vars import variables as vrs

def main():
    """...main!"""
    bot = discord.Client()

    intents = discord.Intents.default()
    intents.members = True

    bot = cmds.Bot(command_prefix=vrs.CMD_PREFIX, intents=intents)
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


    # def test_for_commands(command):
    #     """Prints the commands registered."""
    #     print(bot.all_commands.keys(), command in bot.all_commands.keys())

    # testForCommands("test")

    # Log in
    print("Logging into bot...")
    bot_token = os.environ['FadbToken']
    bot.run(bot_token)

if __name__ == "__main__":
    main()
