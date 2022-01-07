# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use

import nextcord as nx
import nextcord.ext.commands as cmds

import backend.command_related.command_wrapper as c_w
import backend.command_related.choice_param as c_p
import backend.artist_related.library.log_library as l_l


class LogControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c_w.command(
        category = c_w.Categories.artist_management,
        description = "Sets the channel to put the logs on.",
        parameters = {
            "[dump | live]": (
                "Chooses whether or not the log to be put in is the `dump` or `live` log.\n"
                "`Dump` log channels contain new artist requests and accepts / declines to those requests.\n"
                "`Live` log channels are like `dump` log channels, but requests will be deleted once it is accepted or declined."
            )
        },
        req_guild_admin = True
    )
    async def loglocation(self, ctx: cmds.Context, log_type: str, channel: str):
        pass



def setup(bot: nx.Client):
    bot.add_cog(LogControl(bot))