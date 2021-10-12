import discord
import discord.ext.commands as cmds

import main
from Functions import CommandWrappingFunction as cw
from Functions import FirebaseInteraction as fi
from GlobalVariables import defaults

async def updateDatabase():
    guildData: dict = fi.getData(['guildData'])
    for guildClient in main.bot.guilds:
        if not str(guildClient.id) in guildData.keys():
            fi.createData(['guildData', guildClient.id], defaults.default["guildData"]["guildId"])

class Hello(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @cmds.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}.")
        await updateDatabase()
    
    @cmds.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await updateDatabase()

    @cw.command(
        category=cw.Categories.basicCommands,
        description="Updates the database manually.",
        aliases=['ud'],
        requireDev=True
    )
    async def updatedatabase(self, ctx: cmds.Context):
        await updateDatabase()
        await ctx.send("Database updated.")


    @cw.command(
        category=cw.Categories.basicCommands,
        description="Hello...?"
    )
    async def hello(self, ctx):
        await ctx.send(f"...what? I- hmm. Thanks for the... erm... hello... I guess?")


    @cw.command(
        category=cw.Categories.basicCommands,
        description="Ping...?"
    )
    async def ping(self, ctx):
        await ctx.send(f"Pong! <@{ctx.author.id}>")


    @cw.command(
        category=cw.Categories.botControl,
        description="Cause an error...?",
        requireDev=True
    )
    async def causeerror(self, ctx):
        raise TypeError("caused error!")

def setup(bot):
    bot.add_cog(Hello(bot))



