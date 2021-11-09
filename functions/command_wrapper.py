"""Contains functions to wrap the command function."""

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-statements
# pylint: disable=line-too-long
# pylint: disable=unused-argument


import functools as fc
import discord
import discord.ext.commands as cmds

from global_vars import variables as vrs
from functions.databases.firebase import firebase_interaction as f_i
from functions.exceptions import send_error as s_e
from functions.exceptions import custom_exc as c_exc


class Categories:
    """Categories."""
    artist_management = "Artist Management"
    basic_commands = "Basic Commands"
    bot_control = "Bot Control"
    moderation = "Moderation"

class CustomCommandClass:
    """Stored command."""
    def __init__(self):
        self.name: str = ""
        self.help: self.Helps = self.Helps()

    class Helps:
        """All help parameters."""
        def __init__(self):
            self.category: str = ""
            self.description: str = ""
            self.parameters: dict[str, str] = {}
            self.aliases: list[str] = []
            self.guild_only: bool = True
            self.cooldown: self.Cooldown = self.Cooldown()
            self.require: self.Require = self.Require()
            self.show_condition = lambda ctx: True
            self.example_usage: list[str] = []

        class Require:
            """What the command requires to be executed."""
            def __init__(self):
                self.guild_owner: bool = False
                self.guild_admin: bool = False
                self.dev: bool = False

        class Cooldown:
            """Cooldown."""
            length: int = 0
            type: str = cmds.BucketType.channel

class ListOfCommands:
    """Lists all commands."""
    commands_all: dict[Categories, list[str]] = {}
    commands: dict[str, CustomCommandClass] = {}


for attribute in dir(Categories):
    if not attribute.startswith("__"):
        ListOfCommands.commands_all[getattr(Categories, attribute)] = []


def command(
        category=Categories.basic_commands,
        description="TNTz forgot to put a description lmao please ping him",
        parameters: dict[str, str] = None,
        aliases: list[str] = None,
        guild_only=True,
        cooldown=0, cooldown_type="",

        req_guild_owner=False,
        req_guild_admin=False,
        req_dev=False,
        req_pa_mod=False,

        show_condition=lambda ctx: True,
        example_usage: list[str] = None
        ):
    """Wraps a command."""

    def decorator(func):
        @fc.wraps(func)
        async def wrapper(*args, **kwargs):
            # self = args[0]
            ctx: cmds.Context = args[1]

            async def send_error(suffix):
                await s_e.send_error(ctx, vrs.global_bot, f"You don't have proper permissions! {suffix}")
                return


            async def check_pa_mod():
                can_verify = f_i.get_data(['mainData', 'canVerify'])
                devs = f_i.get_data(['mainData', 'devs'])

                if str(ctx.author.id) in can_verify["users"] + devs:
                    return True
                if isinstance(ctx.channel, discord.channel.TextChannel):
                    if str(ctx.guild.id) in can_verify["servers"]:
                        for role in ctx.author.roles:
                            if str(role.id) in can_verify["servers"][str(ctx.guild.id)]:
                                return True
                return False

            async def check_admin():
                try:
                    admin_role = f_i.get_data(['guildData', str(ctx.guild.id), 'adminRole'])
                    admin_role = int(admin_role)
                except c_exc.FirebaseNoEntry:
                    return False

                for role in ctx.author.roles:
                    if role.id == admin_role:
                        return True
                return False

            async def check_owner():
                return ctx.author.id == ctx.guild.owner.id

            async def check_dev():
                devs = f_i.get_data(['mainData', 'devs'])
                return str(ctx.author.id) in devs


            if req_dev:
                if not await check_dev():
                    await send_error("Only developers of this bot may do this command!")
                    return

            if req_pa_mod:
                if not await check_pa_mod():
                    await send_error("Only moderators from official servers may do this command!")
                    return

            if req_guild_owner:
                if not await check_owner():
                    await send_error("Only the server owner can do this command!")
                    return

            if req_guild_admin:
                if not await check_admin():
                    await send_error("Only admins of this server may do this command!")
                    return


            if not show_condition(ctx):
                ctx.command.reset_cooldown(ctx)
                return
            return await func(*args, **kwargs)


        if aliases is None:
            wrapper = cmds.command(name=func.__name__)(wrapper)
        else:
            wrapper = cmds.command(name=func.__name__, aliases=aliases)(wrapper)

        if guild_only:
            wrapper = cmds.guild_only()(wrapper)

        if cooldown > 0:
            wrapper = cmds.cooldown(1, cooldown, cooldown_type)(wrapper)


        cmd = CustomCommandClass()

        cmd.name = func.__name__
        helps = cmd.help

        helps.category = category
        helps.description = description
        helps.parameters = parameters
        helps.aliases = aliases
        helps.cooldown.length = cooldown
        helps.cooldown.type = cooldown_type
        helps.guild_only = guild_only

        require = helps.require
        require.dev = req_dev
        require.guild_admin = req_guild_admin
        require.guild_owner = req_guild_owner
        helps.require = require

        helps.show_condition = show_condition
        helps.example_usage = example_usage

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
