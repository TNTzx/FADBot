"""Where the bot starts its life."""

# pylint: disable=assigning-non-slot

import os
import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import global_vars.loggers as lgr


def log_something(log_str: str):
    """Logs something."""
    print(log_str)
    lgr.log_bot_status.info(log_str)


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
    log_something("Loading cogs...")

    def all_cogs():
        """Returns all cogs."""
        return os.listdir(os.path.join(os.path.dirname(__file__), ".", "cogs"))

    for filename in all_cogs():
        if filename.endswith(".py"):
            if filename == "__init__.py":
                continue
            log_something(f"Loading cog '{filename}'...")
            bot.load_extension(f"cogs.{filename[:-3]}")

    log_something("Loaded all cogs!")


    # def test_for_commands(command):
    #     """Prints the commands registered."""
    #     log_something(bot.all_commands.keys(), command in bot.all_commands.keys())

    # testForCommands("test")

    # Log in
    log_something("Logging into bot...")
    bot_token = os.environ['FadbToken']
    bot.run(bot_token)

if __name__ == "__main__":
    main()
