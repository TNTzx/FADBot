"""Structure extensions."""


from .vadb_info import VADBInfo

from .details.details import Details
from .details.aliases import Alias, Aliases
from .details.image_info import \
    Image, ImageInfo, \
        Proof, DEFAULT_PROOF, \
        Avatar, DEFAULT_AVATAR, \
        Banner, DEFAULT_BANNER, \
    DEFAULT_IMAGE_URL
from .details.music_info import MusicInfo
from .details.socials import Social, Socials

from .states.states import \
    State, StateList, \
        Status, StatusList, \
        Availability, AvailabilityList, \
    States
from .states.usage_rights import UsageRight, UsageRights
