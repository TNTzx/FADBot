# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use

import nextcord as nx
import nextcord.ext.commands as cmds

from global_vars import defaults
from functions import command_wrapper as c_w
from functions.databases.firebase import firebase_interaction as f_i
from functions import other_functions as o_f


async def add_new_to_database(bot):
    """Updates the database for joined servers."""
    guild_data: dict = f_i.get_data(['guildData'])
    for guild_client in bot.guilds:
        if not str(guild_client.id) in guild_data.keys():
            f_i.edit_data(['guildData'], {str(guild_client.id): defaults.default["guildData"]["guildId"]})


class Hello(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmds.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}.")
        tntz = await o_f.get_tntz(self.bot)
        await tntz.send("Logged in!")
        await add_new_to_database(self.bot)

    @cmds.Cog.listener()
    async def on_guild_join(self, guild: nx.Guild):
        await add_new_to_database(self.bot)

    @c_w.command(
        category=c_w.Categories.basic_commands,
        description="Updates the database manually.",
        aliases=['ud'],
        req_dev=True
    )
    async def updatedatabase(self, ctx: cmds.Context):
        await add_new_to_database(self.bot)
        await ctx.send("Database updated.")


    @c_w.command(
        category=c_w.Categories.basic_commands,
        description="Hello...?"
    )
    async def hello(self, ctx):
        await ctx.send("...what? I- hmm. Thanks for the... erm... hello... I guess?")


    @c_w.command(
        category=c_w.Categories.basic_commands,
        description="Ping...?"
    )
    async def ping(self, ctx):
        await ctx.send(f"Pong! <@{ctx.author.id}>")


    @c_w.command(
        category=c_w.Categories.bot_control,
        description="Cause an error...?",
        req_dev=True
    )
    async def causeerror(self, ctx):
        raise TypeError("caused error!")

def setup(bot):
    bot.add_cog(Hello(bot))
