"""Contains logic for checking if a user has enough permissions to use the command."""


import typing as typ

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import backend.firebase as firebase


class Permission():
    """Represents a command permission level."""
    name: str

    @classmethod
    def has_permission(cls, ctx: nx_cmds.Context):
        """Returns `True` if the permission has been met for the current `Context`."""

    @classmethod
    def get_fail_message(cls):
        """Gets the message for when the permission has not been met."""

    @classmethod
    def get_full_fail_message(cls):
        """Gets the full fail message."""
        return (
            "You have insufficient permissions!\n"
            f"{cls.get_fail_message()}"
        )


class Permissions():
    """Contains a list of enabled permissions for this command."""
    def __init__(
            self,
            perms: list[typ.Type[Permission]] | None = None,
            enable_not_ban_perm: bool = True
            ):
        if perms is None:
            perms = []

        if enable_not_ban_perm:
            perms = [PermNotBanned] + perms

        self.perms = perms


    def has_all_perms(self, ctx: nx_cmds.Context):
        """
        Returns `(True, )` if all permissions has been met for the current `Context`.
        Returns `(False, <failed Permission>)` if at least one permission has not been met.
        """
        for perm in self.perms:
            if not perm.has_permission(ctx):
                return (False, perm)

        return (True,)


class PermNotBanned(Permission):
    """Requires the user to not be banned."""
    name = "not banned"

    @classmethod
    def has_permission(cls, ctx: nx_cmds.Context):
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


class PermDev(Permission):
    """Requires the user to be a developer of the bot."""
    name = "VADB developer"
    @classmethod
    def has_permission(cls, ctx: nx_cmds.Context):
        user_id = str(ctx.author.id)
        devs = firebase.get_data(
            firebase.ShortEndpoint.devs.get_path(),
            default = []
        )

        return user_id in devs

    @classmethod
    def get_fail_message(cls):
        return "Only developers of this bot may do this command!"


class PermPAMod(Permission):
    """Requires the user to be a PA moderator by role or by ID."""
    name = "PA moderator"

    @classmethod
    def has_permission(cls, ctx: nx_cmds.Context):
        if PermDev.has_permission(ctx):
            return True

        can_verify_users = firebase.get_data(
            firebase.ENDPOINTS.e_artist.e_change_req.e_can_verify.e_users.get_path(),
            default = []
        )
        user_id = str(ctx.author.id)
        if user_id in can_verify_users:
            return True

        can_verify_roles = firebase.get_data(
            firebase.ENDPOINTS.e_artist.e_change_req.e_can_verify.e_server_roles.get_path(),
            default = []
        )
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


class PermGuildOwner(Permission):
    """Requires the user to be the guild's owner."""
    name = "server owner"

    @classmethod
    def has_permission(cls, ctx: nx_cmds.Context):
        return ctx.author.id == ctx.guild.owner.id

    @classmethod
    def get_fail_message(cls):
        return "Only the server owner can do this command!"


class PermGuildAdmin(Permission):
    """Requires the user to be a guild admin."""
    name = "server admin"

    @classmethod
    def has_permission(cls, ctx: nx_cmds.Context):
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
