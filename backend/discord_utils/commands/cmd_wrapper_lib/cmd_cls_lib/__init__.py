"""Library that contains the command class."""


from .cmd_cls import DiscordCommand

from .cmd_categories import \
    CmdCategory, \
        CategoryArtistManagement, CategoryBasics, CategoryBotControl, CategoryModeration

from .cmd_infos import \
    CmdInfo, \
        CooldownInfo, UsabilityInfo

from .cmd_perms import \
    Permission, Permissions, \
    NotBanned, Dev, PAMod, GuildAdmin, GuildOwner
