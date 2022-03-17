"""Artist structures."""


from .artist import Artist


from .struct_exts import VADBInfo

from .struct_exts.details.details import Details
from .struct_exts.details.aliases import Alias, Aliases
from .struct_exts.details.image_info import \
    Image, ImageInfo, \
        Proof, DEFAULT_PROOF, \
        Avatar, DEFAULT_AVATAR, \
        Banner, DEFAULT_BANNER, \
    DEFAULT_IMAGE_URL
from .struct_exts.details.music_info import MusicInfo
from .struct_exts.details.socials import Social, Socials

from .struct_exts.states.states import \
    State, StateList, \
        Status, StatusList, \
        Availability, AvailabilityList
from .struct_exts.states.usage_rights import UsageRight, UsageRights
