import discord
from discord.ext import commands
import os
import asyncio

class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}.")

    @commands.command(name="hello")
    async def hello(self, ctx):
        await ctx.send(f"...what? I- hmm. Thanks for the... erm... hello... I guess?")

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f"Pong! <@{ctx.author.id}>")

def setup(bot):
    bot.add_cog(Hello(bot))



