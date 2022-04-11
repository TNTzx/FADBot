"""Contains controls for logging artist requests."""


import nextcord.ext.commands as nx_cmds

import global_vars
import backend.discord_utils as disc_utils
import backend.firebase as firebase
import backend.exc_utils as exc_utils

from ... import utils as cog


class CogLogCmds(cog.RegisteredCog):
    """Contains commands for setting log locations."""

    @disc_utils.cmd_wrap.command_wrap(
        category = disc_utils.cmd_wrap.CategoryArtistManagement,
        cmd_info = disc_utils.cmd_wrap.CmdInfo(
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
            perms = disc_utils.cmd_wrap.Permissions(
                [disc_utils.cmd_wrap.GuildAdmin]
            ),
            cooldown_info = disc_utils.CooldownInfo(
                length = 10,
                type_ = nx_cmds.BucketType.guild
            )
        )
    )
    async def loglocationset(self, ctx: nx_cmds.Context, log_type: str, channel_mention: str):
        """Sets the log location."""
        channel = await disc_utils.channel_from_id_warn(ctx, channel_mention)

        await ctx.send("Registering log channel...")

        path_initial = firebase.ENDPOINTS.e_discord.e_guilds.get_path() + [str(ctx.guild.id), "logs", "locations"]
        for channel_id_on in firebase.get_data(path_initial).values():
            if channel_id_on is None:
                continue
            if int(channel_id_on) == channel.id:
                await exc_utils.send_error(ctx, f"This channel is already being used as another log channel! Unregister existing channels using `{global_vars.CMD_PREFIX}loglocationremove`!")
                return


        @disc_utils.choice_param_cmd(ctx, log_type, ["dump", "live"])
        async def log_type_choice():
            firebase.override_data(
                path_initial + [log_type],
                str(channel.id)
            )

        await log_type_choice()

        await ctx.send(f"`{log_type.capitalize()}` log channel registered as {channel.mention}.")


    @disc_utils.cmd_wrap.command_wrap(
        category = disc_utils.cmd_wrap.CategoryArtistManagement,
        cmd_info = disc_utils.cmd_wrap.CmdInfo(
            description = "Unregisters the channel to put the logs on.",
            parameters = {
                "[dump | live]": (
                    "Chooses whether or not the log to be put in is the `dump` or `live` log.\n"
                    "`Dump` log channels contain new artist requests and accepts / declines to those requests.\n"
                    "`Live` log channels are like `dump` log channels, but requests will be deleted once it is accepted or declined."
                )
            },
            aliases = ["llus"],
            perms = disc_utils.cmd_wrap.Permissions(
                [disc_utils.cmd_wrap.GuildAdmin]
            ),
            cooldown_info = disc_utils.CooldownInfo(
                length = 10,
                type_ = nx_cmds.BucketType.guild
            )
        )
    )
    async def loglocationunset(self, ctx: nx_cmds.Context, log_type: str):
        """Unregisters the log channel."""
        await ctx.send("Unregistering log channel...")

        @disc_utils.choice_param_cmd(ctx, log_type, ["dump", "live"])
        async def log_type_choice():
            path_initial = firebase.ENDPOINTS.e_discord.e_guilds.get_path() + [str(ctx.guild.id), "logs", "locations", log_type]

            if firebase.get_data(path_initial) == firebase.PLACEHOLDER_DATA:
                await exc_utils.send_error(ctx, f"There's no registered channel for the `{log_type}` log type for this server! Add one using `{global_vars.CMD_PREFIX}loglocationset`!")
                raise exc_utils.ExitFunction()

            firebase.override_data(path_initial, firebase.PLACEHOLDER_DATA)

        await log_type_choice()

        await ctx.send(f"`{log_type.capitalize()}` log channel unregistered.")
