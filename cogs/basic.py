"""Contains commands run on startup, guild join, etc."""


import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import backend.logging.loggers as lgr
import global_vars.defaults as defaults
import backend.command_related.command_wrapper as c_w
import backend.command_related.is_using as i_u
import backend.firebase as firebase
import backend.exceptions.custom_exc as c_e


async def add_new_to_database():
    """Updates the database for joined servers."""
    endpoint = firebase.ENDPOINTS.e_discord.e_guilds.get_path()
    guild_data: dict = firebase.get_data(endpoint)
    for guild_client in vrs.global_bot.guilds:
        if not str(guild_client.id) in guild_data.keys():
            # TODO needing default values here
            firebase.edit_data(endpoint, {str(guild_client.id): defaults.default["guildData"]["guildId"]})


class Hello(cmds.Cog):
    """Contains commands for stuff."""
    def __init__(self, bot):
        self.bot = bot


    @cmds.Cog.listener()
    async def on_ready(self):
        """Gets called when the bot is ready."""
        print(f"Logged in as {vrs.global_bot.user}.")

        lgr.log_bot_status.info("Logged in.")

        # initialize on ready
        await add_new_to_database()
        i_u.delete_all_is_using()

        vrs.TNTz = await vrs.global_bot.fetch_user(279803094722674693)
        await vrs.TNTz.send("Logged in!")


    @cmds.Cog.listener()
    async def on_guild_join(self, guild: nx.Guild):
        """Gets called whenever the bot joins a server."""
        await add_new_to_database()


    @c_w.command(
        category=c_w.Categories.basic_commands,
        description="Updates the database manually.",
        aliases=['ud'],
        req_dev=True,
        show_help=False
    )
    async def updatedatabase(self, ctx: cmds.Context):
        """Updates the database."""
        await add_new_to_database()
        await ctx.send("Database updated.")


    @c_w.command(
        category=c_w.Categories.basic_commands,
        description="Hello...?"
    )
    async def hello(self, ctx: cmds.Context):
        """well hello there how are u am dog"""
        await ctx.send("...what? I- hmm. Thanks for the... erm... hello... I guess?")


    @c_w.command(
        category=c_w.Categories.basic_commands,
        description="Ping...?"
    )
    async def ping(self, ctx: cmds.Context):
        """WHY WHY WOULD YOU DO THIS"""
        await ctx.send(f"Pong! <@{ctx.author.id}>")


    @c_w.command(
        category=c_w.Categories.bot_control,
        description="Cause an error...?",
        guild_only=False,
        req_dev=True,
        show_help=False
    )
    async def causeerror(self, ctx: cmds.Context):
        """AAAAAAAAAAAAAAAAA"""
        raise ValueError("ERROR RAISED QUYSDKSHK QUICK EVERYTHING'S FALLING DOWN AAAAAAA")

def setup(bot):
    bot.add_cog(Hello(bot))
