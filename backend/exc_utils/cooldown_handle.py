"""Library for handling cooldowns."""


import nextcord.ext.commands as nx_cmds


def reset_cooldown(ctx: nx_cmds.Context):
    """Resets the cooldown."""
    ctx.command.reset_cooldown(ctx)
