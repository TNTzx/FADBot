"""Library that contains the command class."""


from .cmd_cls import DiscordCommand

from .cmd_categories import \
    CmdCategory, \
        ArtistManagement, Basics, BotControl, Moderation

from .cmd_infos import \
    CmdInfo, \
        CooldownInfo, UsabilityInfo

from .cmd_usage_requs import \
    CmdUsageRequ, CmdUsageRequs, \
    NotBanned, Dev, PAMod, GuildAdmin, GuildOwner
