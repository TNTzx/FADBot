"""Contains functions to wrap the command function."""


import functools as fc

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import backend.firebase as firebase
import backend.exc_utils.send_error as s_e
import backend.exc_utils.custom_exc as c_exc


class CmdCategories:
    """Categories."""
    artist_management = "Artist Management"
    basic_commands = "Basic Commands"
    bot_control = "Bot Control"
    moderation = "Moderation"

class CustomCommandClass:
    """Stored command."""
    def __init__(self):
        self.name = ""
        self.help = self.Helps()

    class Helps:
        """All help parameters."""
        def __init__(self):
            self.category = ""
            self.description = ""
            self.parameters: dict[str, str] = {}
            self.aliases: list[str] = []
            self.guild_only = True
            self.cooldown = self.Cooldown()
            self.require = self.Require()
            self.show_condition = lambda ctx: True
            self.show_help = True
            self.example_usage: list[str] = []

        class Require:
            """What the command requires to be executed."""
            def __init__(self):
                self.pa_mod = False
                self.guild_owner = False
                self.guild_admin= False
                self.dev = False

        class Cooldown:
            """Cooldown."""
            length = 0
            type = nx_cmds.BucketType.channel

class ListOfCommands:
    """Lists all commands."""
    commands_all: dict[CmdCategories, list[str]] = {}
    commands: dict[str, CustomCommandClass] = {}


for attribute in dir(CmdCategories):
    if not attribute.startswith("__"):
        ListOfCommands.commands_all[getattr(CmdCategories, attribute)] = []


async def check_pa_mod(ctx: nx_cmds.Context, user_id: int):
    """Checks if a user is a PA Moderator by role or a dev."""
    can_verify_roles = firebase.get_data(
        firebase.ENDPOINTS.e_artist.e_change_req.e_can_verify.e_server_roles.get_path(),
        default = []
    )
    can_verify_users = firebase.get_data(
        firebase.ENDPOINTS.e_artist.e_change_req.e_can_verify.e_users.get_path(),
        default = []
    )
    devs = firebase.get_data(firebase.ENDPOINTS.e_main.e_privileges.e_devs.get_path())

    user_id = str(user_id)

    if user_id in can_verify_users + devs:
        return True
    if isinstance(ctx.channel, nx.channel.TextChannel):
        guild_id = str(ctx.guild.id)
        if guild_id in can_verify_roles:
            for role in ctx.author.roles:
                if str(role.id) in can_verify_roles[guild_id]:
                    return True
    return False

async def check_admin(ctx: nx_cmds.Context, user_id: int):
    """Check if the user is a guild admin."""
    user_id = str(user_id)
    guild_id = str(ctx.guild.id)

    try:
        admin_role = firebase.get_data(firebase.ENDPOINTS.e_discord.e_guilds.get_path() + [guild_id, 'admin_role'])
        admin_role = int(admin_role)
    except firebase.FBNoPath:
        return False

    for role in ctx.author.roles:
        if role.id == admin_role:
            return True
    return False

async def check_owner(ctx: nx_cmds.Context, user_id: int):
    """Check if the user is a guild owner."""
    return user_id == ctx.guild.owner.id

async def check_dev(user_id: int):
    """Check if a user is a dev."""
    user_id = str(user_id)
    devs = firebase.get_data(
        firebase.ENDPOINTS.e_main.e_privileges.e_devs.get_path(),
        default = []
    )

    return user_id in devs

async def check_ban(user_id: int):
    """Checks if the user is banned from the bot."""
    user_id = str(user_id)
    bans = firebase.get_data(
        firebase.ENDPOINTS.e_discord.e_users_general.e_banned_users.get_path(),
        default = []
    )

    return user_id in bans


def command(
        category = CmdCategories.basic_commands,
        description = "TNTz forgot to put a description lmao please ping him",
        parameters: dict[str, str] = None,
        aliases: list[str] = None,
        guild_only = True,
        cooldown = 0, cooldown_type = "",

        req_guild_owner = False,
        req_guild_admin = False,
        req_dev = False,
        req_pa_mod = False,

        show_condition = lambda ctx: True,
        show_help = True,
        example_usage: list[str] = None
        ):
    """Decorator factory to define a command."""

    def decorator(func):
        @fc.wraps(func)
        async def wrapper(*args, **kwargs):
            # self = args[0]
            ctx: nx_cmds.Context = args[1]

            async def send_error(suffix):
                await s_e.send_error(ctx, f"You don't have proper permissions! {suffix}")
                return


            if await check_ban(ctx.author.id):
                await s_e.send_error(ctx, (
                    "You have been banned from using the bot.\n"
                    "Appeal to an official Project Arrhythmia moderator if you wish."
                ))
                return


            if req_dev:
                if not await check_dev(ctx.author.id):
                    await send_error("Only developers of this bot may do this command!")
                    return

            if req_pa_mod:
                if not await check_pa_mod(ctx, ctx.author.id):
                    await send_error("Only moderators from official servers may do this command!")
                    return

            if req_guild_owner:
                if not await check_owner(ctx, ctx.author.id):
                    await send_error("Only the server owner can do this command!")
                    return

            if req_guild_admin:
                if not await check_admin(ctx, ctx.author.id):
                    await send_error("Only admins of this server may do this command!")
                    return


            if not show_condition(ctx):
                ctx.command.reset_cooldown(ctx)
                return
            return await func(*args, **kwargs)


        if aliases is None:
            wrapper = nx_cmds.command(name = func.__name__)(wrapper)
        else:
            wrapper = nx_cmds.command(name = func.__name__, aliases = aliases)(wrapper)

        if guild_only:
            wrapper = nx_cmds.guild_only()(wrapper)

        if cooldown > 0:
            wrapper = nx_cmds.cooldown(1, cooldown, cooldown_type)(wrapper)


        cmd = CustomCommandClass()

        cmd.name = func.__name__
        helps: CustomCommandClass.Helps = cmd.help

        helps.category = category
        helps.description = description
        helps.parameters = parameters if parameters is not None else {}
        helps.aliases = aliases if aliases is not None else []
        helps.cooldown.length = cooldown
        helps.cooldown.type = cooldown_type
        helps.guild_only = guild_only

        require: CustomCommandClass.Helps.Require = helps.require
        require.pa_mod = req_pa_mod
        require.dev = req_dev
        require.guild_admin = req_guild_admin
        require.guild_owner = req_guild_owner
        helps.require = require

        def show_condition_wrapper(ctx: nx_cmds.Context):
            try:
                return show_condition(ctx)
            except AttributeError:
                return False

        helps.show_condition = show_condition_wrapper
        helps.show_help = show_help
        helps.example_usage = example_usage if example_usage is not None else []

        cmd.help = helps

        if cmd.name not in ListOfCommands.commands_all[category]:
            ListOfCommands.commands_all[category].append(cmd.name)

        if cmd.name not in ListOfCommands.commands.keys():
            ListOfCommands.commands[cmd.name] = cmd
        if aliases is not None:
            for alias in aliases:
                if alias not in ListOfCommands.commands.keys():
                    ListOfCommands.commands[alias] = cmd

        return wrapper

    return decorator
