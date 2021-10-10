from discord.ext import commands

import main
from Functions import CommandWrappingFunction as cw
from Functions import FirebaseInteraction as fi


class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}.")


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
        requireGuildAdmin=True
    )
    async def causeerror(self, ctx):
        raise TypeError("caused error!")

def setup(bot):
    bot.add_cog(Hello(bot))



