import discord
import discord.ext.commands as cmds
import functools as fc

from GlobalVariables import variables as vars
from Functions import ExtraFunctions as ef


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
        requireGuildAdmin=False,
        requirePAModerator=False,
        showCondition=lambda ctx: True,
        exampleUsage=[]
        ):
    
    def decorator(func):
        async def conditionAdd(*args, **kwargs):
            ctx: cmds.Context = args[1]
            if requirePAModerator:
                canVerify = vars.canVerify
                serverId = ctx.guild.id

                async def sendError():
                    await ef.sendError(ctx, "You don't have proper moderation permissions! Only moderators from official servers may do this command!")
                    return

                if not serverId in canVerify.keys():
                    await sendError()
                    return

                memberRoles = canVerify[serverId]

                hasCorrectRole = False
                for role in ctx.author.roles:
                    if role.id in memberRoles:
                        hasCorrectRole = True
                        break
                if not hasCorrectRole:
                    await sendError()
                    return

            if not showCondition(args[1]):
                ctx.command.reset_cooldown(ctx)
                return
            return await func(*args, **kwargs)

        wrapped = cmds.command(name=func.__name__, aliases=aliases)(conditionAdd)



        if guildOnly:
            wrapped = cmds.guild_only()(wrapped)

        if cooldown > 0:
            wrapped = cmds.cooldown(1, cooldown, cooldownType)(wrapped)
        
        if requireGuildAdmin:
            wrapped = cmds.has_role(vars.adminRole)(wrapped)


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
            "requireAdmin": requireGuildAdmin,
            "showCondition": showCondition,
            "exampleUsage": exampleUsage
        }
        helpData[category][func.__name__] = cmdData


        return wrapped

    return decorator

