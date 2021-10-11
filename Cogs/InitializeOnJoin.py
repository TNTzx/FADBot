import discord
import discord.ext.commands as cmds

from GlobalVariables import defaults
from Functions import FirebaseInteraction as fi


class InitializeOnJoin(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmds.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if not guild.id in fi.getData(['guildData']).keys():
            fi.createData(['guildData', guild.id], defaults.default["guildData"]["guildId"])


def setup(bot):
    bot.add_cog(InitializeOnJoin(bot))