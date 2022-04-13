"""Contains moderation."""


import nextcord.ext.commands as nx_cmds

import global_vars
import backend.logging.loggers as lgr

import backend.discord_utils as disc_utils
import backend.firebase as firebase
import backend.exc_utils as exc_utils
import backend.other as ot

from ... import utils as cog


class CogModeration(cog.RegisteredCog):
    """Contains controls for moderating stuff about the bot."""

    @disc_utils.command_wrap(
        category = disc_utils.CategoryModeration,
        cmd_info = disc_utils.CmdInfo(
            description = "Sets the admin for the server.",
            params = disc_utils.Params(
                disc_utils.ParamArgument(
                    "role id",
                    description = (
                        "The ID of the role you want to add."
                        "If you don't know how to get IDs, click [here](https://support.discord.com/hc/en-us/community/posts/360048094171/comments/1500000318142)."
                    )
                )
            ),
            perms = disc_utils.Permissions(
                [disc_utils.PermGuildOwner]
            )
        )
    )
    async def setadmin(self, ctx: nx_cmds.Context, role_id):
        """Sets the admin role of this server."""
        try:
            int(role_id)
        except ValueError:
            await exc_utils.send_error(ctx, "You didn't send a valid role ID!")
            return

        firebase.edit_data(
            firebase.ENDPOINTS.e_discord.e_guilds.get_path() + [ctx.guild.id],
            {'admin_role': role_id}
        )
        await ctx.send("The admin role for this server has been set.")


    @disc_utils.command_wrap(
        category = disc_utils.CategoryModeration,
        cmd_info = disc_utils.CmdInfo(
            description = "Bans or unbans a user from using the bot.",
            params = disc_utils.Params(
                disc_utils.ParamsSplit(
                    disc_utils.Params(
                        disc_utils.ParamLiteral(
                            "ban",
                            description = "Denotes banning the user."
                        )
                    ),
                    disc_utils.Params(
                        disc_utils.ParamLiteral(
                            "unban",
                            description = "Denotes unbanning the user."
                        )
                    ),
                    description = "Bans or unbans the user."
                ),
                disc_utils.ParamArgument(
                    "user id",
                    description = "The ID of the user being banned or unbanned."
                )
            ),
            aliases = ["bb"],
            usability_info = disc_utils.UsabilityInfo(
                guild_only = False
            ),
            perms = disc_utils.Permissions(
                [disc_utils.PermPAMod]
            )
        )
    )
    async def botban(self, ctx: nx_cmds.Context, action: str, user_id: int):
        """Bans or unbans a person from using the bot."""
        path_initial = firebase.ENDPOINTS.e_discord.e_users_general.e_banned_users.get_path()
        user = await disc_utils.user_from_id_warn(ctx, user_id)

        if ctx.author.id == user.id:
            await exc_utils.send_error(ctx, "You're banning yourself!! WHY????? **WHYYYYYY????????**")
            return

        @disc_utils.choice_param_cmd(ctx, action, ["ban", "unban"])
        async def action_choice():
            user_name = f"{user.name}#{user.discriminator}"

            async def send_confirm():
                confirm_view = disc_utils.ViewConfirmCancel()
                confirm_message = await ctx.send((
                        f"Are you sure you want to {action} the user `{user_name}`?\n"
                        f"This command will time out in `{ot.format_time(global_vars.Timeouts.long)}`."
                    ), view = confirm_view)

                output_view = await disc_utils.wait_for_view(ctx, confirm_message, confirm_view)

                if output_view.value == disc_utils.ViewOutputValues.CANCEL:
                    await ctx.send("Command cancelled.")
                    raise exc_utils.ExitFunction()


            user_id_str = str(user_id)

            def user_in_ban_list():
                return user_id_str in firebase.get_data(path_initial, default = [])

            if action == "ban":
                if user_in_ban_list():
                    await exc_utils.send_error(ctx, "The user is already banned!")
                    raise exc_utils.ExitFunction()

                await send_confirm()
                firebase.append_data(path_initial, [user_id_str])
                await ctx.send(f"User `{user_name}` has been banned from using this bot.")
                await user.send((
                    "**You have been banned from using this bot.**\n"
                    "Appeal to an official Project Arrhythmia moderator if you wish to attempt to be unbanned."
                ))

                log_message = f"[BAN] {user_name} | {user.id}"
            else:
                if not user_in_ban_list():
                    await exc_utils.send_error(ctx, "The user hasn't been banned yet!")
                    raise exc_utils.ExitFunction()

                await send_confirm()
                firebase.deduct_data(path_initial, [user_id_str])
                await ctx.send(f"User `{user_name}` has been unbanned from using this bot.")
                await user.send("**You have been unbanned from using this bot.**")

                log_message = f"[UNBAN] {user_name} | {user.id}"

            lgr.log_bot_bans.info(log_message)


        await action_choice()
