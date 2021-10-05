from asyncio.tasks import wait
import discord
import discord.ext.commands as cmds

import main
from Functions import CommandWrappingFunction as cw
from Functions import ExtraFunctions as ef

class ArtistControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cw.command(
        category=cw.Categories.artistManagement,
        description=f"Requests an artist to be added to the database. Times out after `{ef.formatTime(60 * 2)}``.",
        aliases=["aa"]
    )
    async def artistadd(self, ctx: cmds.Context):

        async def waitForResponse(message):
            await ctx.author.send(message)
            response = await main.bot.wait_for("message", check=lambda msg: ctx.author.id == msg.author.id, timeout=60 * 2)
            return response

        response = await waitForResponse("Testing...")
        await ctx.send(response.content)


def setup(bot):
    bot.add_cog(ArtistControl(bot))
