# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use


import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import backend.command_related.command_wrapper as c_w
import backend.command_related.choice_param as c_p
import backend.main_library.checks as ch
import backend.databases.firebase.firebase_interaction as f_i
import backend.exceptions.custom_exc as c_e
import backend.exceptions.send_error as s_e


class LogControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c_w.command(
        category = c_w.Categories.artist_management,
        description = "Registers the channel to put the logs on.",
        parameters = {
            "[dump | live]": (
                "Chooses whether or not the log to be put in is the `dump` or `live` log.\n"
                "`Dump` log channels contain new artist requests and accepts / declines to those requests.\n"
                "`Live` log channels are like `dump` log channels, but requests will be deleted once it is accepted or declined."
            ),
            "channel mention": "The channel mention. Make sure it is highlighted blue for the bot to recognize it properly."
        },
        aliases = ["lls"],
        req_guild_admin = True,
        cooldown = 10, cooldown_type = cmds.BucketType.guild
    )
    async def loglocationset(self, ctx: cmds.Context, log_type: str, channel_mention: str):
        channel = await ch.channel_from_mention(ctx, channel_mention)

        await ctx.send("Registering log channel...")

        path_initial = ["guildData", str(ctx.guild.id), "logs", "locations"]
        for channel_id_on in f_i.get_data(path_initial).values():
            if channel_id_on == vrs.PLACEHOLDER_DATA:
                continue
            if int(channel_id_on) == channel.id:
                await s_e.send_error(ctx, f"This channel is already being used as another log channel! Unregister existing channels using `{vrs.CMD_PREFIX}loglocationremove`!")
                return


        @c_p.choice_param_cmd(ctx, log_type, ["dump", "live"])
        async def log_type_choice():
            f_i.override_data(
                path_initial + [log_type],
                str(channel.id)
            )

        await log_type_choice()

        await ctx.send(f"`{log_type.capitalize()}` log channel registered as {channel.mention}.")


    @c_w.command(
        category = c_w.Categories.artist_management,
        description = "Unregisters the specified channel for logging.",
        parameters = {
            "[dump | live]": (
                "Chooses whether or not the log to be put in is the `dump` or `live` log.\n"
                "`Dump` log channels contain new artist requests and accepts / declines to those requests.\n"
                "`Live` log channels are like `dump` log channels, but requests will be deleted once it is accepted or declined."
            )
        },
        aliases = ["llus"],
        req_guild_admin = True,
        cooldown = 10, cooldown_type = cmds.BucketType.guild
    )
    async def loglocationunset(self, ctx: cmds.Context, log_type: str):
        await ctx.send("Unregistering log channel...")

        @c_p.choice_param_cmd(ctx, log_type, ["dump", "live"])
        async def log_type_choice():
            path_initial = ["guildData", str(ctx.guild.id), "logs", "locations", log_type]

            if f_i.get_data(path_initial) == vrs.PLACEHOLDER_DATA:
                await s_e.send_error(ctx, f"There's no registered channel for the `{log_type}` log type for this server! Add one using `{vrs.CMD_PREFIX}loglocationset`!")
                raise c_e.ExitFunction()

            f_i.override_data(path_initial, vrs.PLACEHOLDER_DATA)

        await log_type_choice()

        await ctx.send(f"`{log_type.capitalize()}` log channel unregistered.")


def setup(bot: nx.Client):
    bot.add_cog(LogControl(bot))
