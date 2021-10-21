# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument


import discord
import discord.ext.commands as cmds

import main
from Functions import CommandWrappingFunction as cw
from Functions import FirebaseInteraction as fi
from GlobalVariables import defaults


async def add_new_to_database():
    """Updates the database for joined servers."""
    guild_data: dict = fi.get_data(['guildData'])
    for guild_client in main.bot.guilds:
        if not str(guild_client.id) in guild_data.keys():
            fi.create_data(['guildData', guild_client.id], defaults.default["guildData"]["guildId"])


class Hello(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmds.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}.")
        await add_new_to_database()

    @cmds.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await add_new_to_database()

    @cw.command(
        category=cw.Categories.basic_commands,
        description="Updates the database manually.",
        aliases=['ud'],
        req_dev=True
    )
    async def updatedatabase(self, ctx: cmds.Context):
        await add_new_to_database()
        await ctx.send("Database updated.")


    @cw.command(
        category=cw.Categories.basic_commands,
        description="Hello...?"
    )
    async def hello(self, ctx):
        await ctx.send("...what? I- hmm. Thanks for the... erm... hello... I guess?")


    @cw.command(
        category=cw.Categories.basic_commands,
        description="Ping...?"
    )
    async def ping(self, ctx):
        await ctx.send(f"Pong! <@{ctx.author.id}>")


    @cw.command(
        category=cw.Categories.bot_control,
        description="Cause an error...?",
        req_dev=True
    )
    async def causeerror(self, ctx):
        raise TypeError("caused error!")

def setup(bot):
    bot.add_cog(Hello(bot))
