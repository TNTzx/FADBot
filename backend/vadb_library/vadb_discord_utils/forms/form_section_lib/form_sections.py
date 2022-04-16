"""Form sections."""


from __future__ import annotations

import typing as typ

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import backend.exc_utils as exc_utils
import backend.discord_utils as disc_utils

from .... import artist_lib as a_s
from .... import queries
from .... import excepts
from .... import change_reqs
from .. import form_exc as f_exc
from . import form_section as f_s
from . import section_states as states


class Name(f_s.RawTextSection):
    """The artist name."""
    async def reformat_input(self, ctx: nx_cmds.Context, response: nx.Message | disc_utils.View, section_state: states.SectionState = None):
        response = await super().reformat_input(ctx, response)

        await ctx.author.send("Checking if there are already possible existing artists and requests with this name. This might take a while...")


        def is_name_in_search(query: queries.BaseQuery, search_term: str, get_search_result_name: typ.Callable[[typ.Any], str]):
            """Checks if the name is in the `searched` list."""
            for search_result in query.query_items:
                if get_search_result_name(search_result) == search_term:
                    return True

            return False

        async def send_multiple_confirm(
                query: queries.BaseQuery,
                search_type_plural_str: str,
                ):
            """Sends the confirmation info for multiple artist / requests found."""
            embed_art = query.generate_embed(
                f"Possible Existing {search_type_plural_str.capitalize()} Found!",
                (
                    f"Existing {search_type_plural_str} may have possibly be on its relevant database already!\n"
                    "Please confirm that you are not submitting a duplicate!"
                ),
                (
                    "Click on \"Confirm\" to confirm that you are not submitting a duplicate entry.\n"
                    "Click on \"Back\" to go back and enter a different artist name.\n"
                    "Click on \"Cancel\" to cancel the current command."
                )
            )

            view = disc_utils.ViewConfirmBackCancel()

            message = await ctx.author.send(
                f"Possible existing {search_type_plural_str.capitalize()} found!",
                embed = embed_art,
                view = view
            )

            result_view = await disc_utils.wait_for_view(ctx, message, view)
            result = result_view.value

            if result == disc_utils.ViewOutputValues.CONFIRM:
                await ctx.author.send("Proceeding...")
            if result == disc_utils.ViewOutputValues.BACK:
                await ctx.author.send("Returning...")
                raise f_exc.InvalidSectionResponse()
            if result == disc_utils.ViewOutputValues.CANCEL:
                await exc_utils.cancel_command(ctx, send_author = True)


        async def execute_is_multiple(
                searched: list,
                search_term: str,
                get_search_name: typ.Callable[[typ.Any], str],
                search_type_str: str,
                search_type_plural_str: str,
                ):
            """Executes `is_name_in_search` and `send_multiple_confirm`."""
            if is_name_in_search(searched, search_term, get_search_name):
                await disc_utils.send_error(ctx, f"A {search_type_str} with that name already exists.", send_author = True)
                raise f_exc.InvalidSectionResponse()

            await send_multiple_confirm(searched, search_type_plural_str)


        try:
            searched_requests = change_reqs.RequestQuery.from_search(response)

            def get_req_name(search_req: change_reqs.ChangeRequest):
                """Returns the artist's name of the `ChangeRequest`."""
                return search_req.artist.name

            await execute_is_multiple(
                searched = searched_requests,
                search_term = response,
                get_search_name = get_req_name,
                search_type_str = "request",
                search_type_plural_str = "requests"
            )
        except change_reqs.ChangeReqNotFound:
            await ctx.author.send("No existing request found! Attempting to find existing artists...")


        # TEST test this out, couldn't test earlier because server down
        try:
            searched_artists = a_s.ArtistQuery.from_search(response)

            def get_art_name(search_artist: a_s.Artist):
                """Returns the artist's name of the `Artist`."""
                return search_artist.name

            await execute_is_multiple(
                searched = searched_artists,
                search_term = response,
                get_search_name = get_art_name,
                search_type_str = "artist",
                search_type_plural_str = "artists"
            )
        except excepts.VADBNoSearchResult:
            await ctx.author.send("No existing artist found! Proceeding...")


        return response


    async def edit_artist_with_section(self, ctx: nx_cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.name = await self.send_section(ctx, section_state = section_state)

class Proof(f_s.ImageSection):
    """Artist proof."""
    async def edit_artist_with_section(self, ctx: nx_cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.proof = a_s.Proof(await self.send_section(ctx, section_state = section_state))

class Availability(f_s.ChoiceSection):
    """Artist availability."""
    async def edit_artist_with_section(self, ctx: nx_cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        class AvailabilityView(disc_utils.View):
            """Extra view."""
            @nx.ui.select(placeholder = "Select availability...", options = a_s.AvailabilityList.get_states_options(), row = 0)
            async def avail_choose(self, select: nx.ui.Select, interact: nx.Interaction):
                """a"""
                self.value = select.values
                self.stop()

        response = await self.send_section(ctx, section_state = section_state, extra_view = AvailabilityView)
        artist.states.availability.value = int(response)

value_state_dict = {
    "Verified": True,
    "Disallowed": False
}

class UsageRights(f_s.DictSection):
    """Artist's usage rights."""
    def __init__(self, title: str, description: str, example: str = None, notes: str = None, default_section_state: states.SectionState = states.SectionStates.default):
        super().__init__(title, description, example, notes, default_section_state = default_section_state, allowed_val_func = lambda value: value in list(value_state_dict))

    async def reformat_input(self, ctx: nx_cmds.Context, response: nx.Message | disc_utils.View, section_state: states.SectionState = None):
        diction = await super().reformat_input(ctx, response)
        return {
            key: value_state_dict[value] for key, value in diction.items()
        }

    async def edit_artist_with_section(self, ctx: nx_cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        diction: dict = await self.send_section(ctx, section_state)
        artist.states.usage_rights = a_s.UsageRights(
            [
                a_s.UsageRight(
                    description = description,
                    is_verified = is_verified
                ) for description, is_verified in diction.items()
            ]
        )

class Description(f_s.RawTextSection):
    """Artist description."""
    async def edit_artist_with_section(self, ctx: nx_cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.description = await self.send_section(ctx, section_state = section_state)

class Aliases(f_s.ListSection):
    """Artist's aliases."""
    async def edit_artist_with_section(self, ctx: nx_cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.aliases = a_s.Aliases([
            a_s.Alias(name) for name in await self.send_section(ctx, section_state = section_state)
        ])

class Avatar(f_s.ImageSection):
    """Artist's avatar."""
    async def edit_artist_with_section(self, ctx: nx_cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.image_info.avatar = a_s.Avatar(await self.send_section(ctx, section_state = section_state))

class Banner(f_s.ImageSection):
    """Artist's banner."""
    async def edit_artist_with_section(self, ctx: nx_cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.image_info.banner = a_s.Banner(await self.send_section(ctx, section_state = section_state))

class TrackCount(f_s.NumberSection):
    """Artist's track count."""
    async def edit_artist_with_section(self, ctx: nx_cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.music_info.track_count = await self.send_section(ctx, section_state = section_state)

class Genre(f_s.RawTextSection):
    """Artist's genre."""
    async def edit_artist_with_section(self, ctx: nx_cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.music_info.genre = await self.send_section(ctx, section_state = section_state)

class Socials(f_s.LinksSection):
    """Artist's social links."""
    async def edit_artist_with_section(self, ctx: nx_cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.socials = a_s.Socials(
            [a_s.Social(link) for link in await self.send_section(ctx, section_state = section_state)]
        )

class Notes(f_s.RawTextSection):
    """Artist notes."""
    async def edit_artist_with_section(self, ctx: nx_cmds.Context, artist: a_s.Artist, section_state: states.SectionState = None) -> None:
        artist.details.notes = await self.send_section(ctx, section_state = section_state)


class FormSections():
    """All form sections."""
    name = Name(
        title = "name",
        description = "The artist's name.",
        example = "TheFatRat",
        notes = "You must send the most commonly used name of the artist. You can set other aliases in the `aliases` field.",
    )
    proof = Proof(
        title = "proof of contact",
        description = "The proof that you have for sending this request.",
        notes = "Screenshot your proof that you contacted the artist. Send it here."
    )
    availability = Availability(
        title = "availability",
        description = "Describes the artist's availability.",
    )
    usage_rights = UsageRights(
        title = "usage rights",
        description = "The artist's statement of including / excluding specific songs or albums.",
        example = (
            "Spider Man 2 Pizza Theme: Verified\n"
            "Remixes: Disallowed\n"
            "Under label \"Inconsolata Records\": Disallowed\n"
            "Other songs: Verified"
        ),
        notes = (
            "The **value**s (which are the text to the right of the colon (`:`)) must be either `\"Verified\"` or `\"Disallowed\"`.\n"
            "`\"Verified\"` means this selection of songs or this song is verified and can be used for PA level making.\n"
            "`\"Disallowed\"` means it cannot be used for PA level creation."
        ),
        default_section_state = states.SectionStates.skippable
    )
    description = Description(
        title = "description",
        description = "The artist's description.",
        example = "This is an artist well known for making music listened by everyone.",
        default_section_state = states.SectionStates.skippable
    )
    aliases = Aliases(
        title = "aliases",
        description = "Other names the artist may go by.",
        example = (
            "answearing machine\n"
            "A!NS\n"
            "answearing"
        ),
        default_section_state = states.SectionStates.skippable
    )
    avatar = Avatar(
        title = "avatar",
        description = "The artist's avatar.",
        default_section_state = states.SectionStates.skippable
    )
    banner = Banner(
        title = "banner",
        description = "The artist's banner.",
        default_section_state = states.SectionStates.skippable
    )
    track_count = TrackCount(
        title = "track count",
        description = "The amount of tracks the artist has produced.",
        notes = "This number doesn't need to be accurate.",
        default_section_state = states.SectionStates.skippable
    )
    genre = Genre(
        title = "genre",
        description = "The artist's genre.",
        notes = "If you don't know what genre to put, press \"Skip\".",
        default_section_state = states.SectionStates.skippable
    )
    socials = Socials(
        title = "socials",
        description = "The artist's social links.",
        example = (
            "https://www.youtube.com/channel/UCtxKzA7OSpRh3OX9aJRShUg\n"
            "https://open.spotify.com/artist/1EheS355QusAVqx9Pux9No\n"
            "https://soundcloud.com/similar-outskirts"
        ),
        default_section_state = states.SectionStates.skippable
    )
    notes = Notes(
        title = "notes",
        description = "Other notes you want to put in.",
        example = "Artist may disallow at one point...",
        default_section_state = states.SectionStates.skippable
    )


    @classmethod
    def get_all_form_sections(cls):
        """Returns all form sections."""
        return f_s.FormSection.form_sections

    @classmethod
    def get_all_options(cls):
        """Returns all options of each form section."""
        return [form_section.generate_option() for form_section in cls.get_all_form_sections()]

    @classmethod
    def get_options_view(cls, placeholder: str = "Select attribute..."):
        """Returns the `View` of all options."""
        class ViewFormSections(disc_utils.ViewConfirmCancel):
            """A view for choices."""
            @nx.ui.select(placeholder = placeholder, options = cls.get_all_options())
            async def command_select(self, select: nx.ui.Select, interact: nx.Interaction):
                """Selects!"""
                self.value = select.values
                self.stop()

        return ViewFormSections

    @classmethod
    def get_section_from_title(cls, title: str):
        """Gets the section from the title."""
        for section in cls.get_all_form_sections():
            if section.title == title:
                return section

        raise ValueError(f"\"{title}\" not found.")
