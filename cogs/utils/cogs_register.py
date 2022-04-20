"""Contains functions for registering cogs."""


import nextcord.ext.commands as nx_cmds

import backend.logging as lgr


class RegisteredCog(nx_cmds.Cog):
    """Parent class for all cogs."""
    def __init__(self, bot: nx_cmds.Bot):
        self.bot = bot

    @classmethod
    def get_all_cogs(cls):
        """Gets all cogs."""
        return cls.__subclasses__()


    @classmethod
    def load_all_cogs_to_bot(cls, bot: nx_cmds.Bot):
        """Loads all cogs to a bot."""
        for cog in cls.get_all_cogs():
            log_message = f"Loading cog \"{cog.__name__}\"..."
            print(log_message)
            lgr.log_bot_status.info(log_message)

            bot.add_cog(cog(bot))
