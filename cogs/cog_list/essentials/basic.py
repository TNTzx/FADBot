"""Contains commands run on startup, guild join, etc."""


import nextcord as nx
import nextcord.ext.commands as nx_cmds

import global_vars
import backend.logging.loggers as lgr
import backend.discord_utils as disc_utils
import backend.firebase as firebase

from ... import utils as cog


async def add_new_to_database():
    """Updates the database for joined servers."""
    endpoint = firebase.ENDPOINTS.e_discord.e_guilds
    endpoint_path = endpoint.get_path()

    guild_data: dict = firebase.get_data(endpoint_path)
    for guild_client in global_vars.bot.guilds:
        if not str(guild_client.id) in guild_data.keys():
            firebase.edit_data(endpoint_path, {str(guild_client.id): endpoint.get_default_data()})


class CogBasic(cog.RegisteredCog):
    """Contains commands for basic stuff."""

    @nx_cmds.Cog.listener()
    async def on_ready(self):
        """Gets called when the bot is ready."""
        print(f"Logged in as {global_vars.bot.user}.")

        lgr.log_bot_status.info("Logged in.")

        await add_new_to_database()
        disc_utils.delete_all_is_using()

        global_vars.TNTz = await global_vars.bot.fetch_user(279803094722674693)
        await global_vars.TNTz.send("Logged in!")


    @nx_cmds.Cog.listener()
    async def on_guild_join(self, guild: nx.Guild):
        """Gets called whenever the bot joins a server."""
        await add_new_to_database()


    @disc_utils.command_wrap(
        category = disc_utils.CategoryBasics,
        cmd_info = disc_utils.CmdInfo(
            description = "Updates the database manually.",
            aliases = ["ud"],
            perms = disc_utils.Permissions(
                [disc_utils.GuildOwner]
            ),
            usability_info = disc_utils.UsabilityInfo(
                visible_in_help = False
            )
        )
    )
    async def updatedatabase(self, ctx: nx_cmds.Context):
        """Updates the database."""
        await add_new_to_database()
        await ctx.send("Database updated.")


    @disc_utils.command_wrap(
        category = disc_utils.CategoryBasics,
        cmd_info = disc_utils.CmdInfo(
            description = "Hello...?"
        )
    )
    async def hello(self, ctx: nx_cmds.Context):
        """well hello there how are u am dog"""
        await ctx.send("...what? I- hmm. Thanks for the... erm... hello... I guess?")


    @disc_utils.command_wrap(
        category = disc_utils.CategoryBasics,
        cmd_info = disc_utils.CmdInfo(
            description = "PONG"
        )
    )
    async def ping(self, ctx: nx_cmds.Context):
        """WHY WHY WOULD YOU DO THIS"""
        await ctx.send(f"Pong! <@{ctx.author.id}>")


    @disc_utils.command_wrap(
        category = disc_utils.CategoryBotControl,
        cmd_info = disc_utils.CmdInfo(
            description = "Causes an error!",
            usability_info = disc_utils.UsabilityInfo(
                visible_in_help = False,
                guild_only = False
            )
        )
    )
    async def causeerror(self, ctx: nx_cmds.Context):
        """AAAAAAAAAAAAAAAAA"""
        raise ValueError("ERROR RAISED QUYSDKSHK QUICK EVERYTHING'S FALLING DOWN AAAAAAA")
