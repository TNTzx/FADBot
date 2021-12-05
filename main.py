"""Where the bot starts its life."""

# pylint: disable=assigning-non-slot

import os
import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs


def main():
    """...main!"""
    bot = nx.Client()

    intents = nx.Intents.default()
    intents.reactions = True
    intents.members = True
    intents.guilds = True

    bot = cmds.Bot(command_prefix=vrs.CMD_PREFIX, intents=intents)
    bot.remove_command("help")

    vrs.global_bot = bot


    # Load all cogs
    print("Loading cogs...")

    def all_cogs():
        """Returns all cogs."""
        return os.listdir(os.path.join(os.path.dirname(__file__), ".", "cogs"))

    for filename in all_cogs():
        if filename.endswith(".py"):
            if filename == "__init__.py":
                continue
            print(f"Loading cog '{filename}'...")
            bot.load_extension(f"cogs.{filename[:-3]}")

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
