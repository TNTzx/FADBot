"""Where the bot starts its life."""


import os

import nextcord as nx
import nextcord.ext.commands as cmds

import cogs

import global_vars.variables as vrs
import backend.logging.loggers as lgr


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

    # exclude_cogs = ["artist_control"]
    # def all_cogs():
    #     """Returns all cogs."""
    #     return os.listdir(os.path.join(os.path.dirname(__file__), ".", "cogs"))

    # for filename in all_cogs():
    #     if filename.endswith(".py"):
    #         filename = filename[:-3]
    #         if filename == "__init__":
    #             continue
    #         if filename in exclude_cogs:
    #             log_something(f"WARNING: Not loading cog '{filename}'!")
    #             continue

    #         log_something(f"Loading cog '{filename}'...")
    #         bot.load(f"cogs.{filename}")

    cogs.RegisteredCog.load_all_cogs_to_bot(bot)

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
