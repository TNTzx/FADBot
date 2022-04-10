"""Contains logic for checking if a user has enough usage requirements to use the command."""


import typing as typ

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import backend.firebase as firebase


class CmdUsageRequ():
    """Represents a usage requirement."""
    @classmethod
    def has_met_requ(cls, ctx: nx_cmds.Context):
        """Returns `True` if the usage requirement has been met for the current `Context`."""

    @classmethod
    def get_fail_message(cls):
        """Gets the message for when the requirement has not been met."""

    @classmethod
    def get_full_fail_message(cls):
        """Gets the full fail message."""
        return (
            "You have insufficient permissions!\n"
            f"{cls.get_fail_message()}"
        )


class CmdUsageRequs():
    """Contains a list of enabled usage requirements for this command."""
    def __init__(
            self,
            usage_requs: list[typ.Type[CmdUsageRequ]] | None = None,
            enable_not_ban_requ: bool = True
            ):
        if enable_not_ban_requ:
            usage_requs = [NotBanned] + usage_requs

        self.usage_requs = usage_requs


    def has_met_all_requs(self, ctx: nx_cmds.Context):
        """
        Returns `(True, )` if all usage requirements has been met for the current `Context`.
        Returns `(False, <failed CmdUsageRequ>)` if at least one requirement has not been met.
        """
        for usage_requ in self.usage_requs:
            if not usage_requ.has_met_requ(ctx):
                return (False, usage_requ)

        return (True,)


# TEST test these out
class NotBanned(CmdUsageRequ):
    """Requires the user to not be banned."""
    @classmethod
    def has_met_requ(cls, ctx: nx_cmds.Context):
        user_id = str(ctx.author.id)
        bans = firebase.get_data(
            firebase.ShortEndpoint.discord_users_general.e_banned_users.get_path(),
            default = []
        )

        return not user_id in bans

    @classmethod
    def get_fail_message(cls):
        return (
            "You have been banned from using the bot.\n"
            "Appeal this ban to an official Project Arrhythmia moderator if you wish."
        )


class Dev(CmdUsageRequ):
    """Requires the user to be a developer of the bot."""
    @classmethod
    def has_met_requ(cls, ctx: nx_cmds.Context):
        user_id = str(ctx.author.id)
        devs = firebase.get_data(
            firebase.ShortEndpoint.devs.get_path(),
            default = []
        )

        return user_id in devs

    @classmethod
    def get_fail_message(cls):
        return "Only developers of this bot may do this command!"


class PAMod(CmdUsageRequ):
    """Requires the user to be a PA moderator by role or by ID."""
    @classmethod
    def has_met_requ(cls, ctx: nx_cmds.Context):
        can_verify_roles = firebase.get_data(
            firebase.ENDPOINTS.e_artist.e_change_req.e_can_verify.e_server_roles.get_path(),
            default = []
        )
        can_verify_users = firebase.get_data(
            firebase.ENDPOINTS.e_artist.e_change_req.e_can_verify.e_users.get_path(),
            default = []
        )
        devs = firebase.get_data(firebase.ENDPOINTS.e_main.e_privileges.e_devs.get_path())

        user_id = str(ctx.author.id)

        if user_id in can_verify_users + devs:
            return True
        if isinstance(ctx.channel, nx.channel.TextChannel):
            guild_id = str(ctx.guild.id)
            if guild_id in can_verify_roles:
                for role in ctx.author.roles:
                    if str(role.id) in can_verify_roles[guild_id]:
                        return True
        return False

    @classmethod
    def get_fail_message(cls):
        return "Only Project Arrhythmia moderators can do this command!"


class GuildOwner(CmdUsageRequ):
    """Requires the user to be the guild's owner."""
    @classmethod
    def has_met_requ(cls, ctx: nx_cmds.Context):
        return ctx.author.id == ctx.guild.owner.id

    @classmethod
    def get_fail_message(cls):
        return "Only the server owner can do this command!"


class GuildAdmin(CmdUsageRequ):
    """Requires the user to be a guild admin."""
    @classmethod
    def has_met_requ(cls, ctx: nx_cmds.Context):
        guild_id = str(ctx.guild.id)

        try:
            admin_role = firebase.get_data(firebase.ShortEndpoint.discord_guilds.get_path() + [guild_id, 'admin_role'])
            admin_role = int(admin_role)
        except firebase.FBNoPath:
            return False

        for role in ctx.author.roles:
            if role.id == admin_role:
                return True
        return False

    @classmethod
    def get_fail_message(cls):
        return "Only admins of this server may do this command!"
