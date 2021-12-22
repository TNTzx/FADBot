# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use

import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import global_vars.loggers as lgr
import global_vars.defaults as defaults
import functions.command_related.command_wrapper as c_w
import functions.command_related.is_using as i_u
import functions.databases.firebase.firebase_interaction as f_i


async def add_new_to_database():
    """Updates the database for joined servers."""
    guild_data: dict = f_i.get_data(['guildData'])
    for guild_client in vrs.global_bot.guilds:
        if not str(guild_client.id) in guild_data.keys():
            f_i.edit_data(['guildData'], {str(guild_client.id): defaults.default["guildData"]["guildId"]})


class Hello(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmds.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {vrs.global_bot.user}.")
        vrs.TNTz = await vrs.global_bot.fetch_user(279803094722674693)
        await vrs.TNTz.send("Logged in!")

        lgr.log_bot_status.info("Logged in.")

        # initialize on ready
        await add_new_to_database()
        i_u.delete_all_is_using()

    @cmds.Cog.listener()
    async def on_guild_join(self, guild: nx.Guild):
        await add_new_to_database()

    @c_w.command(
        category=c_w.Categories.basic_commands,
        description="Updates the database manually.",
        aliases=['ud'],
        req_dev=True,
        show_help=False
    )
    async def updatedatabase(self, ctx: cmds.Context):
        await add_new_to_database()
        await ctx.send("Database updated.")


    @c_w.command(
        category=c_w.Categories.basic_commands,
        description="Hello...?"
    )
    async def hello(self, ctx):
        await ctx.send("...what? I- hmm. Thanks for the... erm... hello... I guess?")


    @c_w.command(
        category=c_w.Categories.basic_commands,
        description="Ping...?"
    )
    async def ping(self, ctx):
        await ctx.send(f"Pong! <@{ctx.author.id}>")


    @c_w.command(
        category=c_w.Categories.bot_control,
        description="Cause an error...?",
        guild_only=False,
        req_dev=True,
        show_help=False
    )
    async def causeerror(self, ctx):
        raise TypeError("caused error!")

def setup(bot):
    bot.add_cog(Hello(bot))
