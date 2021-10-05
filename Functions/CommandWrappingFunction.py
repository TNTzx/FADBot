import discord
import discord.ext.commands as cmds
import functools as fc

from GlobalVariables import variables as vars


class Categories:
    artistManagement = "Artist Management"
    basicCommands = "Basic Commands"
    botControl = "Bot Control"


helpData = {}

for attribute in dir(Categories):
    if not attribute.startswith("__"):
        helpData[getattr(Categories, attribute)] = {}


def command(
        category=Categories.basicCommands,
        description="TNTz forgot to put a description lmao please ping him",
        parameters={},
        aliases=[],
        guildOnly=True,
        cooldown=0, cooldownType="",
        requireAdmin=False,
        showCondition=lambda ctx: True,
        exampleUsage=[]
        ):
    
    def decorator(func):
        @fc.wraps(func)
        async def wrapper(*args, **kwargs):
            if not showCondition(args[1]):
                args[1].command.reset_cooldown(args[1])
                return
            return await func(*args, **kwargs)


        wrapper = cmds.command(name=func.__name__, aliases=aliases)(wrapper)

        if guildOnly:
            wrapper = cmds.guild_only()(wrapper)

        if cooldown > 0:
            wrapper = cmds.cooldown(1, cooldown, cooldownType)(wrapper)
        
        if requireAdmin:
            wrapper = cmds.has_role(vars.adminRole)(wrapper)


        cdTypeGotten = cooldownType
        if cdTypeGotten == cmds.BucketType.user:
            cdTypeGot = "User"
        elif cdTypeGotten == cmds.BucketType.guild:
            cdTypeGot = "Entire Server"
        else:
            cdTypeGot = "Not Defined"


        cmdData = {
            "description": description,
            "parameters": parameters,
            "aliases": aliases,
            "guildOnly": guildOnly,
            "cooldown": {
                "length": cooldown,
                "type": cdTypeGot
            },
            "requireAdmin": requireAdmin,
            "showCondition": showCondition,
            "exampleUsage": exampleUsage
        }
        helpData[category][func.__name__] = cmdData


        return wrapper

    return decorator

