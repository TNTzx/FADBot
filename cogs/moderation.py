# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use


# import nextcord as nx
import nextcord.ext.commands as cmds

import functions.databases.firebase.firebase_interaction as f_i
import functions.command_related.command_wrapper as c_w
import functions.exceptions.send_error as s_e

class Moderation(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c_w.command(
        category=c_w.Categories.moderation,
        description="Sets the admin for the server.",
        parameters={"id": "The ID of the role you want to add. If you don't know how to get IDs, click [here](https://support.discord.com/hc/en-us/community/posts/360048094171/comments/1500000318142)."},
        req_guild_owner=True
    )
    async def setadmin(self, ctx: cmds.Context, role_id):
        try:
            int(role_id)
        except ValueError:
            await s_e.send_error(ctx, "You didn't send a valid role ID!")
            return

        f_i.edit_data(['guildData', ctx.guild.id], {'adminRole': role_id})
        await ctx.send("The admin role for this server has been set.")


def setup(bot):
    bot.add_cog(Moderation(bot))
