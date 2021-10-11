import discord
import discord.ext.commands as cmds
import functools as fc

from Functions import FirebaseInteraction as fi
from GlobalVariables import variables as varss
from Functions import ExtraFunctions as ef
from Functions import CustomExceptions as ce


class Categories:
    artistManagement = "Artist Management"
    basicCommands = "Basic Commands"
    botControl = "Bot Control"
    moderation = "Moderation"


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

        requireGuildOwner=False,
        requireGuildAdmin=False,
        requireDev=False,
        requirePAModerator=False,

        showCondition=lambda ctx: True,
        exampleUsage=[]
        ):
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            self = args[0]
            ctx: cmds.Context = args[1]

            async def sendError(suffix):
                await ef.sendError(ctx, f"You don't have proper permissions! {suffix}")
                return

            if requireDev:
                if not ctx.author.id in varss.devs:
                    await sendError("Only developers of this bot may do this command!")
                    return

            if requirePAModerator:
                canVerify = varss.canVerify

                async def checkVerify():
                    if ctx.author.id in canVerify["users"]:
                        return True
                    if ctx.guild.id in canVerify["servers"]:
                        for role in ctx.author.roles:
                            if role.id in canVerify["servers"][ctx.guild.id]:
                                return True
                    return False

                if not await checkVerify():
                    await sendError("Only moderators from official servers may do this command!")
                    return

            if requireGuildOwner:
                if not ctx.author == ctx.guild.owner:
                    await sendError("Only the server owner can do this command!")
            
            if requireGuildAdmin:
                async def checkAdmin():
                    try:
                        adminRoles = fi.getData(['guildData', ctx.guild.id, 'adminRole'])
                    except ce.FirebaseNoEntry:
                        return False

                    for role in ctx.author.roles:
                        if role in adminRoles:
                            return True
                    return False
                
                if not await checkAdmin():
                    await sendError("Only admins of this server may do this command!")
                    return

            if not showCondition(ctx):
                ctx.command.reset_cooldown(ctx)
                return
            return await func(*args, **kwargs)

        wrapped = cmds.command(name=func.__name__, aliases=aliases)(wrapper)



        if guildOnly:
            wrapped = cmds.guild_only()(wrapped)

        if cooldown > 0:
            wrapped = cmds.cooldown(1, cooldown, cooldownType)(wrapped)


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

