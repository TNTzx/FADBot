# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use

import nextcord as nx
import nextcord.ext.commands as cmds
import requests as req

import global_vars.variables as vrs
import backend.main_classes.choice_param as c_p
import backend.command_related.command_wrapper as c_w
import backend.command_related.is_using as i_u
import backend.artist_related.checks as a_ch
import backend.artist_related.library.artist_library as a_l
import backend.artist_related.library.log_library as l_l
import backend.databases.firebase.firebase_interaction as f_i
import backend.exceptions.send_error as s_e
import backend.exceptions.custom_exc as c_e
import backend.other_functions as o_f


class ArtistControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot


    @c_w.command(
        category=c_w.Categories.artist_management,
        description="Requests an artist to be added to the database.",
        aliases=["ara"],
        guild_only=False
    )
    @i_u.sustained_command()
    async def artistrequestadd(self, ctx: cmds.Context, *skips):
        if not isinstance(ctx.channel, nx.channel.DMChannel):
            await ctx.send("The artist add request form is sent to your DMs. Please check it.")

        await ctx.author.send("Reminder that this bot is made for a website!\nCheck it out! https://fadb.live/")
        await ctx.author.send("> The artist add request is now being set up. Please __follow all instructions as necessary.__")

        data = a_l.Default()
        if "no_init" in skips:
            pass
        else:
            await data.trigger_all_set_attributes(ctx)

        if "no_edit" in skips:
            pass
        else:
            await data.edit_loop(ctx)

        if "no_send" in skips:
            data.vadb_info.artist_id = 0
        else:
            try:
                await ctx.author.send("Creating verification submission...")
                response = a_l.VADB.Send.Create(data).send_data()
                artist_id = response["data"]["id"]
                await ctx.author.send("Applying details...")
                a_l.VADB.Send.Edit(data).send_data(artist_id)
                data.vadb_info.artist_id = artist_id
            except req.exceptions.HTTPError:
                await s_e.send_error(ctx, "The artist may already be pending, or this artist already exists! I warned you about it! >:(", send_author=True)
                return

        await ctx.author.send("The `add request` has been submitted. Please wait for an official moderator to approve your submission.")

        await data.post_log(l_l.LogTypes.PENDING, ctx.author.id)


    @c_w.command(
        category=c_w.Categories.artist_management,
        description="Requests an artist to be edited in the database.",
        parameters={
            "id": "Artist ID to edit."
        },
        aliases=["are"],
        guild_only=False
    )
    @i_u.sustained_command()
    async def artistrequestedit(self, ctx: cmds.Context, artist_id: int):
        if not isinstance(ctx.channel, nx.channel.DMChannel):
            await ctx.send("The artist `edit request` form is sent to your DMs. Please check it.")

        artist = await a_ch.get_artist_by_id(ctx, artist_id)
        await artist.edit_loop(ctx)

        await ctx.author.send("Sending `edit request`...")
        a_l.Firebase.Logging(artist).send_data(l_l.LogTypes.EDITING)
        await ctx.author.send("The `edit request` has been submitted. Please wait for an official moderator to approve your submission.")

        await artist.post_log(l_l.LogTypes.EDITING, ctx.author.id)


    @c_w.command(
        category=c_w.Categories.artist_management,
        description="Accepts / declines the request.",
        parameters={
            "[\"add\" / \"edit\"]": "Chooses whether or not the request to be verified is to `add` an artist or `edit` an artist.",
            "id": "Artist ID to verify.",
            "[\"accept\" / \"decline\"]": "Accepts or declines the verification submission. `accept` to mark the artist as completed, or `decline` to delete the submission.",
            "reason": "Reason for declining the verification submission. Only required if you choose `decline`. Surround with quotes."
        },
        aliases=["av"],
        guild_only=False,
        req_pa_mod=True
    )
    @i_u.sustained_command()
    async def artistverify(self, ctx: cmds.Context, _type: str, artist_id: int, action: str, reason: str = None):
        artist = await a_ch.get_artist_by_id(ctx, artist_id)

        if artist.states.status.get_name() != "Pending":
            await s_e.send_error(ctx, f"The artist `{artist.name}` is not pending! You must have an artist that is pending!")
            return

        async def send_logs_and_dms(logs_message: str, dm_message: str):
            await ctx.send(logs_message, embed=await artist.generate_embed())
            log_list = artist.discord_info.logs.pending

            if log_list is None:
                return
            if len(log_list) == 0:
                return

            user_ids = []
            for log in log_list:
                if log.user_id not in user_ids:
                    user_ids.append(str(log.user_id))

            users = [await vrs.global_bot.fetch_user(int(user_id)) for user_id in user_ids]
            for user in users:
                await user.send(dm_message, embed=await artist.generate_embed())

            await artist.post_log_to_channels(logs_message, f_i.get_data(["logData", "dump"]))

            return users

        async def confirm_verify(artist_obj: a_l.Default):
            class Confirm(nx.ui.View):
                def __init__(self):
                    super().__init__()
                    self.value = None

                @nx.ui.button(label="Confirm", style=nx.ButtonStyle.green)
                async def confirm(self, button: nx.ui.Button, interact: nx.Interaction):
                    self.value = True
                    self.stop()

                @nx.ui.button(label="Cancel", style=nx.ButtonStyle.red)
                async def cancel(self, button: nx.ui.Button, interact: nx.Interaction):
                    self.value = False
                    self.stop()

            timeout = 60

            confirm = Confirm()
            await ctx.send(f"Are you sure that you want to `{action}` this `{_type} request`?\nThis command times out in `{o_f.format_time(timeout)}`.")
            message = await ctx.send(embed=await artist.generate_embed(), view=confirm)

            def check_button(interact: nx.Interaction):
                return ctx.author.id == interact.user.id and interact.message.id == message.id

            await vrs.global_bot.wait_for("interaction", check=check_button, timeout=timeout)

            if confirm.value:
                return
            await ctx.send("Cancelled.")
            raise c_e.ExitFunction("Exited Function.")


        @c_p.choice_param_cmd(ctx, _type, ["add", "edit"])
        async def _type_choice():
            if _type == "add":
                @c_p.choice_param_cmd(ctx, action, ["accept", "decline"])
                async def action_choice():
                    await confirm_verify(artist)

                    if action == "accept":
                        artist.states.status.value = 0

                        await ctx.send("Verifying `add request`...")
                        a_l.VADB.Send.Edit(artist).send_data(artist.vadb_info.artist_id)
                        await send_logs_and_dms(f"The `add request` has been accepted for `{artist.name}`!", f"Your pending `add request` for `{artist.name}` has been accepted!")
                    if action == "decline":
                        if reason is None:
                            await s_e.send_error(ctx, "You didn't provide a reason as to why the `add request` was declined.")
                            return
                        artist.states.status.value = 1

                        await ctx.send("Declining `add request`...")
                        a_l.VADB.Send.Delete(artist).send_data()
                        await send_logs_and_dms(f"The `add request` has been declined for `{artist.name}` due to the following reason: `{reason}`.", f"Your pending `add request` for `{artist.name}` has been denied due to the following reason:\n`{reason}`")

                await action_choice()
            elif _type == "edit":
                artist_from_vadb = a_l.get_artist_by_id_fb(l_l.LogTypes.EDITING, artist.vadb_info.artist_id)

                @c_p.choice_param_cmd(ctx, action, ["accept", "decline"])
                async def action_choice():
                    await confirm_verify(artist_from_vadb)

                    if action == "accept":
                        await ctx.send("Verifying `edit request`...")
                        a_l.VADB.Send.Edit(artist_from_vadb).send_data(artist_from_vadb.vadb_info.artist_id)
                        await send_logs_and_dms(f"The `edit request` has been accepted for `{artist_from_vadb.name}`!", f"Your pending `edit request` for `{artist_from_vadb.name}` has been accepted!")
                    if action == "decline":
                        if reason is None:
                            await s_e.send_error(ctx, "You didn't provide a reason as to why the `edit request` was declined.")
                            return
                        await send_logs_and_dms(f"The `edit request` has been declined for `{artist_from_vadb.name}` due to the following reason: `{reason}`.", f"Your pending `edit request` for `{artist_from_vadb.name}` has been denied due to the following reason:\n`{reason}`")

                await action_choice()

        await _type_choice()

        await artist.delete_logs()


    @c_w.command(
        category=c_w.Categories.artist_management,
        description="Gets a specified artist by search term or VADB ID.",
        parameters={
            "[<search term> | <ID>]": "If <search term> is used, then the command will return a list of artists for that search term.\nIf <ID> is used, then the bot will return the artist with that ID."
        },
        aliases=["as"],
        guild_only=False,
        cooldown=5, cooldown_type=cmds.BucketType.user,
        example_usage=[
            "##artistsearch \"Some Random Artist Name\"",
            "##artistsearch 5"
        ]
    )
    async def artistsearch(self, ctx: cmds.Context, term: str | int):
        try:
            term = int(term)
        except (ValueError, TypeError):
            pass

        await ctx.send("Searching for artist...")

        if isinstance(term, int):
            artist = await a_ch.get_artist_by_id(ctx, term)
            await ctx.send(embed=await artist.generate_embed())
            return

        search_result = a_l.search_for_artist(term)
        if search_result is None:
            await s_e.send_error(ctx, "Your search term has no results. The artist might also be pending, in which case you can try `##artistsearch <id>` instead. Try again?")
            return

        if len(search_result) == 1:
            await ctx.send(embed=await search_result[0].generate_embed())
        elif len(search_result) > 1:
            await ctx.send("Multiple artists found! Use `##artistsearch <id>` to search for a specific artist.", embed=a_l.generate_search_embed(search_result))


    # @c_w.command(
    #     category=c_w.Categories.bot_control,
    #     description="Cancels the current command. Usually used for artist commands.",
    #     guild_only=False
    # )
    # async def cancel(self, ctx: cmds.Context):
    #     if isinstance(ctx.channel, nx.DMChannel):
    #         await i_u.delete_is_using_command(ctx.author.id)
    #         await ctx.author.send("Command cancelled.")


def setup(bot: cmds.Bot):
    bot.add_cog(ArtistControl(bot))
