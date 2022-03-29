# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use


# import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import backend.logging.loggers as lgr
import backend.command_related.command_wrapper as c_w
import backend.command_related.choice_param as c_p
import backend.utils.views as vw
import backend.utils.asking.wait_for as w_f
import backend.utils.checks as ch
import backend.firebase as firebase
import backend.exceptions.custom_exc as c_e
import backend.exceptions.send_error as s_e
import backend.other_functions as o_f


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

        firebase.edit_data(
            firebase.ENDPOINTS.e_discord.e_guilds.get_path() + [ctx.guild.id],
            {'adminRole': role_id}
        )
        await ctx.send("The admin role for this server has been set.")


    @c_w.command(
        category = c_w.Categories.moderation,
        description = "Bans or unbans a user from using the bot.",
        parameters = {
            "[\"ban\" / \"unban\"]": "`ban`s or `unban`s the user.",
            "user id": "The ID of the user being `ban`ned or `unban`ned."
        },
        aliases = ["bb"],
        req_pa_mod = True,
        guild_only = False
    )
    async def botban(self, ctx: cmds.Context, action: str, user_id: int):
        path_initial = firebase.ENDPOINTS.e_discord.e_users_general.e_banned_users.get_path()

        user = await ch.get_user_from_id(ctx, user_id)

        if ctx.author.id == user.id:
            await s_e.send_error(ctx, "You're banning yourself!! WHY????? **WHYYYYYY????????**")
            return

        @c_p.choice_param_cmd(ctx, action, ["ban", "unban"])
        async def action_choice():
            user_name = f"{user.name}#{user.discriminator}"

            async def send_confirm():
                confirm_view = vw.ViewConfirmCancel()
                confirm_message = await ctx.send((
                        f"Are you sure you want to {action} the user `{user_name}`?\n"
                        f"This command will time out in `{o_f.format_time(vrs.Timeouts.long)}`."
                    ), view=confirm_view)

                output_view = await w_f.wait_for_view(ctx, confirm_message, confirm_view)

                if output_view.value == vw.OutputValues.cancel:
                    await ctx.send("Command cancelled.")
                    raise c_e.ExitFunction()


            user_id_str = str(user_id)

            def user_in_ban_list():
                return user_id_str in firebase.get_data(path_initial)

            if action == "ban":
                if user_in_ban_list():
                    await s_e.send_error(ctx, "The user is already banned!")
                    raise c_e.ExitFunction()

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
                    await s_e.send_error(ctx, "The user hasn't been banned yet!")
                    raise c_e.ExitFunction()

                await send_confirm()
                firebase.deduct_data(path_initial, [user_id_str])
                await ctx.send(f"User `{user_name}` has been unbanned from using this bot.")
                await user.send("**You have been unbanned from using this bot.**")

                log_message = f"[UNBAN] {user_name} | {user.id}"
            
            lgr.log_bot_bans.info(log_message)


        await action_choice()



def setup(bot):
    bot.add_cog(Moderation(bot))
