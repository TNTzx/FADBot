import discord
import discord.ext.commands as cmds

from Functions import FirebaseInteraction as fi
from Functions import CommandWrappingFunction as cw
from Functions import ExtraFunctions as ef

class Moderation(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cw.command(
        category=cw.Categories.moderation,
        description="Sets the admin for the server.",
        parameters={"id": "The ID of the role you want to add. If you don't know how to get IDs, click [here](https://support.discord.com/hc/en-us/community/posts/360048094171/comments/1500000318142)."},
        requireGuildOwner=True
    )
    async def setadmin(self, ctx: cmds.Context, id):
        try:
            int(id)
        except ValueError:
            await ef.sendError(ctx, "You didn't send a valid role ID!")
            return

        fi.editData(['guildData', ctx.guild.id], {'adminRole': id})
        await ctx.send("The admin role for this server has been set.")


def setup(bot):
    bot.add_cog(Moderation(bot))