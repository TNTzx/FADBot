"""Form sections."""


import nextcord as nx
import nextcord.ext.commands as cmds

import backend.utils.views as vw

from .... import artist_structs as a_s
from . import form_section as f_s
from . import section_states as states


class Name(f_s.RawTextSection):
    """The artist name."""
    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View):
        input = await super().reformat_input(ctx, response)

        ...

        return input


    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.name = await self.send_section(ctx, section_state = section_state)

NAME = Name(
    title = "name",
    description = "The artist's name.",
    example = "TheFatRat",
    notes = "You must send the most commonly used name of the artist. You can set other aliases in the `aliases` field.",
)


class Proof(f_s.ImageSection):
    """Artist proof."""
    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.proof = a_s.Proof.from_url(await self.send_section(ctx, section_state = section_state))

PROOF = Proof(
    title = "proof",
    description = "The proof that you have for sending this request.",
    notes = "Screenshot your proof that you contacted the artist. Send it here."
)


class Availability(f_s.ChoiceSection):
    """Artist availability."""
    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        class AvailabilityView(vw.View):
            """Extra view."""
            @nx.ui.select(placeholder="Select availability...", options = a_s.AvailabilityList.get_states_options(), row = 0)
            async def avail_choose(self, select: nx.ui.Select, interact: nx.Interaction):
                """a"""
                self.value = select.values
                self.stop()

        response = await self.send_section(ctx, section_state = section_state, extra_view = AvailabilityView)
        ...

AVAILABILITY = Availability(
    title = "availability",
    description = "Describes the artist's availability.",
)


value_state_dict = {
    "Verified": True,
    "Disallowed": False
}

class UsageRights(f_s.DictSection):
    """Artist's usage rights."""
    def __init__(self, title: str, description: str, example: str = None, notes: str = None, default_section_state: states.SectionState = states.SectionStates.default):
        super().__init__(title, description, example, notes, default_section_state = default_section_state, allowed_val_func = lambda value: value in list(value_state_dict.keys()))

    async def reformat_input(self, ctx: cmds.Context, response: nx.Message | vw.View):
        diction = await super().reformat_input(ctx, response)
        return {
            key: value_state_dict[value] for key, value in diction.items()
        }

    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        diction: dict = await self.send_section(ctx, section_state)
        artist.states.usage_rights = a_s.UsageRights(
            [
                a_s.UsageRight(
                    description = description,
                    is_verified = is_verified
                ) for description, is_verified in diction.items()
            ]
        )

USAGE_RIGHTS = UsageRights(
    title = "usage rights",
    description = "The artist's usage rights. Used to include and exclude specific songs.",
    example = (
        "Remixes: Unverified\n"
        "Other songs: Verified"
    ),
    default_section_state = states.SectionStates.skippable
)


class Description(f_s.RawTextSection):
    """Artist description."""
    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.description = await self.send_section(ctx, section_state = section_state)

DESCRIPTION = Description(
    title = "description",
    description = "The artist's description.",
    example = "This is an artist well known for making music listened by everyone.",
    default_section_state = states.SectionStates.skippable
)


class Aliases(f_s.ListSection):
    """Artist's aliases."""
    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.aliases = a_s.Aliases([
            a_s.Alias(name) for name in await self.send_section(ctx, section_state = section_state)
        ])

ALIASES = Aliases(
    title = "aliases",
    description = "Other names the artist may go by.",
    example = (
        "answearing machine\n"
        "A!NS\n"
        "answearing"
    ),
    default_section_state = states.SectionStates.skippable
)


class Avatar(f_s.ImageSection):
    """Artist's avatar."""
    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.image_info.avatar = a_s.Avatar.from_url(await self.send_section(ctx, section_state = section_state))

AVATAR = Avatar(
    title = "avatar",
    description = "The artist's avatar.",
    default_section_state = states.SectionStates.skippable
)


class Banner(f_s.ImageSection):
    """Artist's banner."""
    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.image_info.banner = a_s.Banner.from_url(await self.send_section(ctx, section_state = section_state))

BANNER = Banner(
    title = "banner",
    description = "The artist's banner.",
    default_section_state = states.SectionStates.skippable
)


class TrackCount(f_s.NumberSection):
    """Artist's track count."""
    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.music_info.track_count = await self.send_section(ctx, section_state = section_state)

TRACK_COUNT = TrackCount(
    title = "track count",
    description = "The amount of tracks the artist has produced.",
    notes = "This number doesn't need to be accurate.",
    default_section_state = states.SectionStates.skippable
)


class Genre(f_s.RawTextSection):
    """Artist's genre."""
    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.music_info.genre = await self.send_section(ctx, section_state = section_state)

GENRE = Genre(
    title = "genre",
    description = "The artist's genre.",
    notes = "If you don't know what genre to put, press \"Skip\".",
    default_section_state = states.SectionStates.skippable
)


class Socials(f_s.LinksSection):
    """Artist's social links."""
    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.socials = a_s.Socials(
            [a_s.Social(link) for link in await self.send_section(ctx, section_state = section_state)]
        )

SOCIALS = Socials(
    title = "socials",
    description = "The artist's social links.",
    example = (
        "https://www.youtube.com/channel/UCtxKzA7OSpRh3OX9aJRShUg\n"
        "https://open.spotify.com/artist/1EheS355QusAVqx9Pux9No\n"
        "https://soundcloud.com/similar-outskirts"
    ),
    default_section_state = states.SectionStates.skippable
)


class Notes(f_s.RawTextSection):
    """Artist notes."""
    async def edit_artist_with_section(self, ctx: cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.notes = await self.send_section(ctx, section_state = section_state)

NOTES = Notes(
    title = "notes",
    description = "Other notes you want to put in.",
    example = "Artist may disallow at one point...",
    default_section_state = states.SectionStates.skippable
)
