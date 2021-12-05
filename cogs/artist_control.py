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
import functions.command_related.command_wrapper as c_w
import functions.artist_related.classes.artist_library as a_l
import functions.artist_related.classes.log_library as l_l
import functions.artist_related.is_using as i_u
import functions.databases.firebase.firebase_interaction as f_i
import functions.exceptions.send_error as s_e
import functions.other_functions as o_f


class ArtistControl(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot


    @c_w.command(
        category=c_w.Categories.artist_management,
        description=f"Requests an artist to be added to the database. Times out after `{o_f.format_time(60 * 2)}`.",
        aliases=["aa"],
        guild_only=False
    )
    async def artistadd(self, ctx: cmds.Context, *skips):
        if await i_u.check_if_using_command(ctx.author.id):
            await s_e.send_error(ctx, f"You're already using this command! Use {vrs.CMD_PREFIX}cancel on your DMs with me to cancel the command.")
            return

        await i_u.add_is_using_command(ctx.author.id)

        if not isinstance(ctx.channel, nx.channel.DMChannel):
            await ctx.send("The form is being set up in your DMs. Please check it.")

        await ctx.author.send("Reminder that this bot is made for a website!\nCheck it out! https://fadb.live/")
        await ctx.author.send("> The artist verification form is now being set up. Please __follow all instructions as necessary.__")

        data = a_l.ArtistStructures.Default()
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
                response = a_l.ArtistStructures.VADB.Send.Create(data).send_data()
                artist_id = response["data"]["id"]
                await ctx.author.send("Applying details...")
                a_l.ArtistStructures.VADB.Send.Edit(data).send_data(artist_id)
                data.vadb_info.artist_id = artist_id
            except req.exceptions.HTTPError:
                await s_e.send_error(ctx, "The artist may already be pending, or this artist already exists! I warned you about it! >:(", send_author=True)
                await i_u.delete_is_using_command(ctx.author.id)
                return

        await ctx.author.send("The artist verification form has been submitted. Please wait for an official moderator to approve your submission.")
        await i_u.delete_is_using_command(ctx.author.id)

        await data.post_log(l_l.LogTypes.PENDING, ctx.author.id)


    @c_w.command(
        category=c_w.Categories.artist_management,
        description="Accepts / declines the verification submission.",
        parameters={
            "id": "Artist ID to verify.",
            "[accept / decline]": "Accepts or declines the verification submission. `accept` to mark the artist as completed, or `decline` to delete the submission.",
            "reason": "Reason for declining the verification submission. Only required if you choose `decline`. Surround with quotes."
        },
        aliases=["av"],
        guild_only=False,
        req_pa_mod=True
    )
    async def artistverify(self, ctx: cmds.Context, artist_id: int, action: str, reason: str = None):
        try:
            artist: a_l.ArtistStructures.Default = a_l.get_artist_by_id(artist_id)
        except req.exceptions.HTTPError:
            await s_e.send_error(ctx, "The artist doesn't exist. Try again?")
            return

        if artist.states.status.get_name() != "Pending":
            await s_e.send_error(ctx, f"The artist `{artist.name}` is not pending! You must have an artist that is pending!")
            return

        action = action.lower()
        if action not in ("accept", "decline"):
            await s_e.send_error(ctx, f"Make sure you have the correct parameters! `{action}` is not a valid parameter.")
            return

        async def send_logs_and_dms(logs_message: str, dm_message: str):
            await ctx.send(logs_message, embed=await artist.generate_embed())
            log_list = artist.discord_info.logs.pending
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

        if action == "accept":
            artist.states.status.value = 0
            a_l.ArtistStructures.VADB.Send.Edit(artist).send_data(artist.vadb_info.artist_id)
            await send_logs_and_dms(f"The add request has been accepted for `{artist.name}`!", f"Your pending add request for `{artist.name}` has been accepted!")
        if action == "decline":
            if reason is None:
                await s_e.send_error(ctx, "You didn't provide a reason as to why the add request was declined.")
                return
            artist.states.status.value = 1
            a_l.ArtistStructures.VADB.Send.Delete(artist).send_data()
            await send_logs_and_dms(f"The verification submission has been declined for `{artist.name}` due to the following reason: `{reason}`.", f"Your pending add request for `{artist.name}` has been denied due to the following reason: `{reason}`")

        await artist.delete_logs()


    @c_w.command(
        category=c_w.Categories.artist_management,
        description="Gets a specified artist.",
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
        search_result = a_l.search_for_artist(term)
        try:
            term = int(term)
        except (ValueError, TypeError):
            pass

        if isinstance(term, int):
            try:
                artist: a_l.ArtistStructures.Default = a_l.get_artist_by_id(term)
                await ctx.send(embed=await artist.generate_embed())
            except req.exceptions.HTTPError:
                await s_e.send_error(ctx, "The artist doesn't exist. Try again?")
            return

        if search_result is None:
            await s_e.send_error(ctx, "Your search term has no results. The artist might also be pending, in which case you can try `##artistsearch <id>` instead. Try again?")
            return

        if len(search_result) == 1:
            await ctx.send(embed=await search_result[0].generate_embed())
        elif len(search_result) > 1:
            await ctx.send("Multiple artists found! Use `##artistsearch <id>` to search for a specific artist.", embed=a_l.generate_search_embed(search_result))


    @c_w.command(
        category=c_w.Categories.bot_control,
        description="Cancels the current command. Usually used for artist commands.",
        guild_only=False
    )
    async def cancel(self, ctx: cmds.Context):
        if isinstance(ctx.channel, nx.DMChannel):
            await i_u.delete_is_using_command(ctx.author.id)
            await ctx.author.send("Command cancelled.")


def setup(bot: cmds.Bot):
    bot.add_cog(ArtistControl(bot))
