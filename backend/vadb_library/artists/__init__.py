"""Artist structures."""


# TODO make this cleaner

from .artist import Artist

from .artist_exts import VADBInfo

from .artist_exts.details.details import Details
from .artist_exts.details.aliases import Alias, Aliases
from .artist_exts.details.image_info import \
    Image, ImageInfo, \
        Proof, DEFAULT_PROOF, \
        Avatar, DEFAULT_AVATAR, \
        Banner, DEFAULT_BANNER, \
    DEFAULT_IMAGE_URL
from .artist_exts.details.music_info import MusicInfo
from .artist_exts.details.socials import Social, Socials

from .artist_exts.states.states import \
    State, StateList, \
        Status, StatusList, \
        Availability, AvailabilityList
from .artist_exts.states.usage_rights import UsageRight, UsageRights

from .artist_query import ArtistQuery
