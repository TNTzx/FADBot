"""Module that contains the classes for the artist data structures."""

# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=useless-super-delegation
# pylint: disable=unused-import
# pylint: disable=invalid-name


from __future__ import annotations
import urllib.parse as ul
import requests as req
import nextcord as nx
import nextcord.ext.commands as cmds

import tldextract as tld

import global_vars.variables as vrs
import backend.main_library.dataclass as dt
import backend.main_library.message_pointer as m_p
import backend.main_library.asking.wait_for as w_f
import backend.main_library.views as vw
import backend.main_library.other as mot
import backend.artist_related.library.log_library as l_l
import backend.artist_related.library.states_library as s_l
import backend.artist_related.library.ask_for_attr.ask_attr as ask_a
import backend.artist_related.library.ask_for_attr.views as a_f_a_v
import backend.databases.firebase.firebase_interaction as f_i
import backend.databases.vadb.vadb_interact as v_i
import backend.exceptions.custom_exc as c_exc
import backend.exceptions.send_error as s_e
import backend.other_functions as o_f


DEFAULT_IMAGE = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"

class ArtistStructure(dt.Dataclass):
    """Parent class where Artist Dataclasses are inherited."""

    def get_json_dict(self):
        """Turns the data into a dictionary for sending."""
        data: dict = self.get_dict()
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = str(value)

        return data

class Default(dt.StandardDataclass, ArtistStructure):
    """Main artist data structure. Must initiate first.
    name: str
    proof: str
    vadb_info: VADBInfo
    states: States
    details: Details
    """

    def __init__(self, data=None):
        super().__init__()
        self.name = "default name"
        self.proof = DEFAULT_IMAGE
        self.vadb_info = self.VADBInfo()
        self.discord_info = self.DiscordInfo()
        self.states = self.States()
        self.details = self.Details()

        self.get_logs()

    class VADBInfo(dt.DataclassSub):
        """Stores VADB-Related info.
        artist_id: int
        page: str
        """
        def __init__(self):
            super().__init__()
            self.artist_id = None
            self.page = "https://fadb.live/"

    class DiscordInfo(dt.DataclassSub):
        """Stores Discord-related info.
        logs: list[o_f.Log]
        """
        def __init__(self):
            super().__init__()
            self.logs = self.Logs()

        class Logs(dt.DataclassSub):
            """Stores logs.
            pending: list[o_f.Log]
            editing: list[o_f.Log]"""
            def __init__(self):
                super().__init__()
                self.pending = [l_l.Log()]
                self.editing = [l_l.Log()]

    class States(dt.DataclassSub):
        """Stores the state of the artist in the verification process.\n
        status: int
        availability: int
        usage_rights: list[dict[str, Any]]
        """
        def __init__(self):
            super().__init__()
            status_dict = {status.value: status.label for status in s_l.status_list}
            self.status: mot.Match = mot.Match(status_dict, 2)

            availability_dict = {avail.value: avail.label for avail in s_l.availability_list}
            self.availability: mot.Match = mot.Match(availability_dict, 2)

            self.usage_rights: list[dict[str, str]] = None

    class Details(dt.DataclassSub):
        """Stores details of the artist.
        description: str
        notes: str
        aliases: list[dict[str, str]]
        images: Images
        music_info: MusicInfo
        socials: list[dict[str, Any]]
        """
        def __init__(self):
            super().__init__()
            self.description = None
            self.notes = None
            self.aliases = [self.Alias()]
            self.images = self.Images()
            self.music_info = self.MusicInfo()
            self.socials = None

        class Alias(dt.DataclassSub):
            """Stores an alias."""
            def __init__(self) -> None:
                super().__init__()
                self.name = None

        class Images(dt.DataclassSub):
            """Stores the images of the artist.
            avatar_url: str
            banner_url: str
            """
            def __init__(self):
                super().__init__()
                self.avatar_url = DEFAULT_IMAGE
                self.banner_url = DEFAULT_IMAGE

        class MusicInfo(dt.DataclassSub):
            """Stores the information about the artist's music.
            tracks: int
            genre: str
            """
            def __init__(self):
                super().__init__()
                self.tracks = 0
                self.genre = None

    def dict_from_nonstandard(self,
            data: VADB.Send.Create | VADB.Send.Edit | VADB.Receive | Firebase.Logging):

        if isinstance(data, VADB.Send.Create):
            return {
                "name": data.name,
                "states": {
                    "status": data.status,
                    "availability": data.availability
                }
            }
        elif isinstance(data, VADB.Send.Edit):
            return {
                "name": data.name,
                "states": {
                    "status": data.status,
                    "availability": data.availability,
                    "usage_rights": data.usageRights
                },
                "details": {
                    "description": data.description,
                    "notes": data.notes,
                    "aliases": data.aliases,
                    "images": {
                        "avatar_url": data.avatarUrl,
                        "banner_url": data.bannerUrl
                    },
                    "music_info": {
                        "tracks": data.tracks,
                        "genre": data.genre
                    },
                    "socials": data.socials
                }
            }
        elif isinstance(data, VADB.Receive):
            return {
                "name": data.name,
                "vadb_info": {
                    "artist_id": data.id,
                    "page": f"https://fadb.live/artist/{data.id}"
                },
                "states": {
                    "status": data.status,
                    "availability": data.availability,
                    "usage_rights": data.usageRights
                },
                "details": {
                    "description": data.description,
                    "notes": data.notes,
                    "aliases": data.aliases,
                    "images": {
                        "avatar_url": data.details.avatarUrl,
                        "banner_url": data.details.bannerUrl
                    },
                    "music_info": {
                        "tracks": data.tracks,
                        "genre": data.genre
                    },
                    "socials": data.details.socials
                }
            }


    def __eq__(self, other: Default):
        if self.__class__ != other.__class__:
            return False

        self_new = self
        other_new = other

        self_new.discord_info.logs = None
        other_new.discord_info.logs = None
        return dt.Dataclass.__eq__(self_new, other_new)



    async def generate_embed(self):
        """Generates an embed."""

        embed = nx.Embed()
        embed.title = f"Artist data for {self.name}:"
        embed.description = "_ _"

        id_format = self.vadb_info.artist_id if self.vadb_info.artist_id is not None else "Not submitted yet!"

        embed.set_author(
            name=f"{self.name} (ID: {id_format})",
            url=self.vadb_info.page,
            icon_url=self.details.images.avatar_url
        )

        embed.set_thumbnail(url=self.details.images.avatar_url)
        embed.set_image(url=self.details.images.banner_url)

        embed.add_field(name="Name:", value=f"**{self.name}**")


        aliases = self.details.aliases

        if aliases != Default().details.aliases:
            aliases = [alias.name for alias in aliases if o_f.is_not_blank_str(alias.name)]
            if o_f.is_not_empty(aliases):
                aliases = f"`{'`, `'.join(aliases)}`"
            else:
                aliases = "No aliases!"
        else:
            aliases = "No aliases!"
        embed.add_field(name="Aliases:", value=aliases)


        description = self.details.description
        description = description if o_f.is_not_blank_str(description) else "No description!"
        embed.add_field(name="Description:", value=description, inline=False)

        vadb_page = self.vadb_info.page
        vadb_page = f"[Click here!]({vadb_page})" if vadb_page != Default().vadb_info.page and o_f.is_not_blank_str(vadb_page) else "Not submitted yet!"
        embed.add_field(name="VADB Page:", value=vadb_page, inline=False)


        status = self.states.status.get_name()
        status = f"**__{status}__**"
        embed.add_field(name="Status:", value=status, inline=False)

        availability = self.states.availability.get_name()
        availability = f"**__{availability}__**"
        embed.add_field(name="Availability:", value=availability)

        usage_rights = self.states.usage_rights
        if o_f.is_not_empty(usage_rights):
            usage_list = []
            for entry in usage_rights:
                status_rights = entry["value"]
                usage_list.append(f"{entry['name']}: {'Verified' if status_rights else 'Disallowed'}")
            usage_rights = "\n".join(usage_list)
        else:
            usage_rights = "No other specific usage rights!"
        embed.add_field(name="Specific usage rights:", value=f"`{usage_rights}`")


        socials = self.details.socials
        if o_f.is_not_empty(socials):
            socials_list = []
            for entry in socials:
                link_type: str = entry["type"]
                link_type = link_type.capitalize()
                link = entry["link"]
                socials_list.append(f"[{link_type}]({link})")
            socials = " ".join(socials_list)
        else:
            socials = "No socials links!"
        embed.add_field(name="Social links:", value=socials, inline=False)

        notes = self.details.notes
        notes = notes if o_f.is_not_blank_str(notes) else "No other notes!"
        embed.add_field(name="Other notes:", value=notes)

        color_keys = {
            "green": 0x00FF00,
            "red": 0xFF0000,
            "yellow": 0xFFFF00,
            "blue": 0x0000FF
        }
        color_match = mot.Match(color_keys, "green")

        if self.states.status.value == 0: # completed
            if self.states.availability.value == 0: # verified
                color_match.value = "green"
            elif self.states.availability.value == 1: # disallowed
                color_match.value = "red"
            elif self.states.availability.value == 2: # contact required
                color_match.value = "yellow"
            elif self.states.availability.value == 3: # varies
                color_match.value = "blue"
        elif self.states.status.value == 1: # no contact
            color_match.value = "red"
        elif self.states.status.value == 2: # pending
            color_match.value = "yellow"

        embed.colour = color_match.get_name()

        return embed


    class Attributes:
        """Contains identifiers for the set_attribute() function."""
        name = mot.Unique()
        proof = mot.Unique()
        availability = mot.Unique()
        usage_rights = mot.Unique()
        description = mot.Unique()
        notes = mot.Unique()
        aliases = mot.Unique()
        avatar_url = mot.Unique()
        banner_url = mot.Unique()
        tracks = mot.Unique()
        genre = mot.Unique()
        socials = mot.Unique()

    async def set_attribute(self, ctx: cmds.Context, attr: mot.Unique, skippable=False):
        """Sets an attribute in this class."""

        attributes = self.Attributes

        def check(attrib):
            return attr == attrib

        if check(attributes.name):
            name = await ask_a.ask_attribute(ctx,
                "Artist Name",
                "Send the artist name.",
                ask_a.OutputTypes.text,
                skippable=skippable
            )

            if name is None:
                return

            search_result = search_for_artist(name)
            if search_result is not None:
                view = a_f_a_v.ViewConfirmCancel()
                message = await ctx.author.send((
                    "Other artist(s) found with this name. Please check if you have a duplicate submission.\n"
                    "Use the `Confirm` button to continue, but make sure that the artist name is unique!\n"
                    "Use the `Cancel` button if the artist is already listed below.\n"
                    "If you are submitting an artist with the same exact name as these results, try to add extra characters on the name to avoid duplicates."
                    ), embed=generate_search_embed(search_result), view=view)

                response = await w_f.wait_for_view(ctx, message, view)
                if response.value == a_f_a_v.OutputValues.cancel:
                    await s_e.cancel_function(ctx, send_author=True)

            if name is not None:
                self.name = name

        elif check(attributes.proof):
            proof = await ask_a.ask_attribute(ctx,
                "Please send proof that you contacted the artist.",
                "Take a screenshot of the email/message that the artist sent you that proves the artist's verification/unverification. You can only upload 1 image/link.",
                ask_a.OutputTypes.image,
                skippable=skippable
            )
            if proof is not None:
                self.proof = proof

        elif check(attributes.availability):
            options_list = [avail.get_option() for avail in s_l.availability_list]
            class AvailabilityChoose(vw.View):
                """Options!"""
                @nx.ui.select(placeholder="Select availability...", options=options_list, row=0)
                async def avail_choose(self, select: nx.ui.Select, interact: nx.Interaction):
                    """a"""
                    self.value = select.values
                    self.stop()

            availability = await ask_a.ask_attribute(ctx,
                "Is the artist verified, disallowed, or does it vary between songs?",
                "This determines whether the artist's songs are allowed for use or not.",
                ask_a.OutputTypes.choice,
                add_view = AvailabilityChoose,
                skippable = skippable
            )

            if availability is not None:
                self.states.availability.value = o_f.get_value_from_key(self.states.availability.data_dict, availability.value[0])

        elif check(attributes.usage_rights):
            usage_rights = await ask_a.ask_attribute(ctx,
                "What are the usage rights for the artist?",
                "This is where you put in the usage rights. For example, if remixes aren't allowed, you can type in `\"Remixes: Disallowed\"`. Add more items as needed.",
                ask_a.OutputTypes.dictionary, choices_dict=["Verified", "Disallowed"],
                skippable=True
            )
            usage_list = []
            if usage_rights is not None:
                for right, state in usage_rights.items():
                    value = state == "verified"
                    usage_list.append({
                        "name": right,
                        "value": value
                    })
                self.states.usage_rights = usage_list

        elif check(attributes.description):
            description = await ask_a.ask_attribute(ctx,
                "Send a description about the artist.",
                "You can put information about the artist here. Their bio, how their music is created, etc. could work.",
                ask_a.OutputTypes.text,
                skippable=True
            )
            if description is not None:
                self.details.description = description

        elif check(attributes.notes):
            notes = await ask_a.ask_attribute(ctx,
                "Notes",
                "Send other notes you want to put in.",
                ask_a.OutputTypes.text,
                skippable=True
            )
            if notes is not None:
                self.details.notes = notes

        elif check(attributes.aliases):
            aliases = await ask_a.ask_attribute(ctx,
                "Artist Aliases",
                "Send other names that the artist goes by.",
                ask_a.OutputTypes.listing,
                skippable=True
            )
            if aliases is not None:
                self.details.aliases = [Default.Details.Alias().from_dict({"name": alias}) for alias in aliases]

        elif check(attributes.avatar_url):
            avatar_url = await ask_a.ask_attribute(ctx,
                "Send an image to an avatar of the artist.",
                "This is the profile picture that the artist uses.",
                ask_a.OutputTypes.image,
                skippable=True
            )
            if avatar_url is not None:
                self.details.images.avatar_url = avatar_url

        elif check(attributes.banner_url):
            banner = await ask_a.ask_attribute(ctx,
                "Send an image to the banner of the artist.",
                "This is the banner that the artist uses.",
                ask_a.OutputTypes.image,
                skippable=True
            )
            if banner is not None:
                self.details.images.banner_url = banner

        elif check(attributes.tracks):
            tracks = await ask_a.ask_attribute(ctx,
                "How many tracks does the artist have?",
                "This is the count for how much music the artist has produced. It can easily be found on Soundcloud pages, if you were wondering.",
                ask_a.OutputTypes.number,
                skippable=True
            )
            if tracks is not None:
                self.details.music_info.tracks = tracks

        elif check(attributes.genre):
            genre = await ask_a.ask_attribute(ctx,
                "What is the genre of the artist?",
                "This is the type of music that the artist makes.",
                ask_a.OutputTypes.text,
                skippable=True
            )
            if genre is not None:
                self.details.music_info.genre = genre

        elif check(attributes.socials):
            socials = await ask_a.ask_attribute(ctx,
                "Put some links for the artist's social media here.",
                "This is where you put in links for the artist's socials such as Youtube, Spotify, Bandcamp, etc.",
                ask_a.OutputTypes.links,
                skippable=True
            )
            social_list = []
            if socials is not None:
                for link in socials:
                    type_link: str = tld.extract(link).domain
                    social_list.append({
                        "link": link,
                        "type": type_link
                    })
                self.details.socials = social_list

    async def edit_loop(self, ctx: cmds.Context):
        """Initiates an edit loop to edit the attributes."""
        attributes = self.Attributes
        command_dict = {
                "Proof": attributes.proof,
                "Availability": attributes.availability,
                "Name": attributes.name,
                "Aliases": attributes.aliases,
                "Description": attributes.description,
                "Avatar URL": attributes.avatar_url,
                "Banner URL": attributes.banner_url,
                "Tracks": attributes.tracks,
                "Genre": attributes.genre,
                "Usage Rights": attributes.usage_rights,
                "Socials": attributes.socials,
                "Notes": attributes.notes
            }


        choices = [nx.SelectOption(label=command_label) for command_label in command_dict]

        class Commands(a_f_a_v.ViewConfirmCancel):
            """A view for choices."""
            @nx.ui.select(placeholder="Select attribute to edit...", options=choices)
            async def command_select(self, select: nx.ui.Select, interact: nx.Interaction):
                """Selects!"""
                self.value = select.values
                self.stop()

        while True:
            view = Commands()

            await ctx.author.send((
                "This is the generated artist profile.\n"
                "Select from the dropdown menu to edit that property."
                "Click on `Confirm` to finish editing the artist."
                "Click on `Cancel` to cancel the command."
            ))
            
            await ctx.author.send(embed = await self.generate_embed())
            message = await ctx.author.send(self.proof, view=view)

            new_view = await w_f.wait_for_view(ctx, message, view)

            if new_view.value == a_f_a_v.OutputValues.confirm:
                return
            elif new_view.value == a_f_a_v.OutputValues.cancel:
                await s_e.cancel_function(ctx, send_author=True)
            elif isinstance(new_view.value[0], str):
                await self.set_attribute(ctx, command_dict[new_view.value[0]],skippable=True)

    async def trigger_all_set_attributes(self, ctx: cmds.Context):
        """Triggers all attributes."""
        async def trigger(cmd):
            await self.set_attribute(ctx, cmd)

        await trigger(self.Attributes.name)
        # add check for existing artist here
        await trigger(self.Attributes.proof)
        await trigger(self.Attributes.availability)
        await trigger(self.Attributes.usage_rights)
        await trigger(self.Attributes.aliases)
        await trigger(self.Attributes.description)
        await trigger(self.Attributes.avatar_url)
        await trigger(self.Attributes.banner_url)
        await trigger(self.Attributes.tracks)
        await trigger(self.Attributes.genre)
        await trigger(self.Attributes.socials)
        await trigger(self.Attributes.notes)


    async def post_log_to_channels(self, prefix: str, channel_dicts, user_id: int = None):
        "Posts logs to channels."
        log_messages = []
        for channel_dict in channel_dicts:
            if not isinstance(channel_dict, dict):
                continue

            channel: nx.TextChannel = vrs.global_bot.get_channel(int(channel_dict["channel"]))
            if channel is None:
                continue
            main_message: nx.Message = await channel.send(prefix, embed=await self.generate_embed())

            proof_message: nx.Message = await channel.send(self.proof)

            log_message = {
                    "main": m_p.MessagePointer(channel_id=channel.id, message_id=main_message.id).get_dict(),
                    "proof": m_p.MessagePointer(channel_id=channel.id, message_id=proof_message.id).get_dict(),
                }

            log_messages.append(log_message)

        return [l_l.Log().from_dict({
            "message": log_message,
            "user_id": str(user_id)
        }) for log_message in log_messages]

    async def post_log(self, log_type: l_l.LogTypes.Pending | l_l.LogTypes.Editing, user_id: int):
        """Posts logs to channels by type."""
        prefix = f"{log_type.title_str} The PA moderators will look into this."
        await self.post_log_to_channels(prefix, f_i.get_data(["logData", "dump"]))
        live_logs = await self.post_log_to_channels(prefix, f_i.get_data(["logData", "live"]), user_id=user_id)
        if log_type == l_l.LogTypes.PENDING:
            self.discord_info.logs.pending = live_logs
        elif log_type == l_l.LogTypes.EDITING:
            self.discord_info.logs.editing = live_logs

        Firebase.Logging(self).send_data(log_type)

    def get_logs(self):
        """Merges object from logs in Firebase."""
        if self.vadb_info.artist_id is None:
            return None

        def get_logs_by_type(log_type: l_l.LogTypes.Base, other: str):
            try:
                return create_log_list(f_i.get_data(log_type.path + [self.vadb_info.artist_id, "discord_info", "logs", other]))
            except c_exc.FirebaseNoEntry:
                return None

        self.discord_info.logs.pending = get_logs_by_type(l_l.LogTypes.PENDING, "pending")
        self.discord_info.logs.editing = get_logs_by_type(l_l.LogTypes.EDITING, "editing")

    async def delete_logs(self):
        """Deletes logs from Discord and Firebase."""
        async def delete_log(log_list: list[l_l.Log], log_type: l_l.LogTypes.Base):
            if log_list is None:
                return

            for log in log_list:
                main_message = await log.message.main.get_message()
                proof_message = await log.message.proof.get_message()
                if None in [main_message, proof_message]:
                    continue
                await main_message.delete()
                await proof_message.delete()

            try:
                f_i.delete_data(log_type.path + [str(self.vadb_info.artist_id)])
            except c_exc.FirebaseNoEntry:
                pass

        self.discord_info.logs.pending = await delete_log(self.discord_info.logs.pending, l_l.LogTypes.PENDING)
        self.discord_info.logs.editing = await delete_log(self.discord_info.logs.editing, l_l.LogTypes.EDITING)


class VADB:
    """Contains classes for VADB Interaction."""

    class Send:
        """Contains classes for sending data to VADB's API."""

        class Create(dt.NonStandardDataclass, ArtistStructure):
            """Data structure for sending the "create artist" request.
            name: str
            status: int
            availability: int"""

            default_class = Default

            def __init__(self, data=None):
                super().__init__()
                self.name = None
                self.status = None
                self.availability = None

            def dict_from_default(self, data: Default):
                return {
                    "name": data.name,
                    "status": data.states.status.value,
                    "availability": data.states.availability.value
                }

            def send_data(self):
                """Creates the artist using the current instance."""
                return v_i.make_request("POST", "/artist/", self.get_json_dict())

        class Edit(dt.NonStandardDataclass, ArtistStructure):
            """Data structure for sending the "edit artist" request."""

            default_class = Default

            def __init__(self, datas=None):
                super().__init__()
                self.name = None
                self.status = None
                self.availability = None
                self.usageRights = None
                self.aliases = None
                self.description = None
                self.notes = None
                self.tracks = None
                self.genre = None
                self.avatarUrl = None
                self.bannerUrl = None
                self.socials = None

            def dict_from_default(self, data: Default):
                return {
                        "name": data.name,

                        "status": data.states.status.value,
                        "availability": data.states.availability.value,
                        "usageRights": data.states.usage_rights,

                        "aliases": [{"name": alias.name} for alias in data.details.aliases],
                        "description": data.details.description,
                        "notes": data.details.notes,
                        "tracks": data.details.music_info.tracks,
                        "genre": data.details.music_info.genre,
                        "avatarUrl": data.details.images.avatar_url,
                        "bannerUrl": data.details.images.banner_url,
                        "socials": data.details.socials
                    }

            def send_data(self, artist_id):
                """Edits the artist using the current instance."""
                return v_i.make_request("PATCH", f"/artist/{artist_id}", self.get_json_dict())


        class Delete(dt.NonStandardDataclass, ArtistStructure):
            """Data structure for requesting to completely obliterate the artist from the database.
            id: int"""

            default_class = Default

            def __init__(self, datas=None):
                super().__init__()
                self.artist_id = None

            def dict_from_default(self, data: Default):
                return {
                    "artist_id": data.vadb_info.artist_id
                }

            def send_data(self):
                """Completely obliterates the artist from the database."""
                return v_i.make_request("DELETE", f"/artist/{self.artist_id}")

    class Receive(dt.NonStandardDataclass, ArtistStructure):
        """Data structure for a received response from VADB's API.
        id: int
        name: str
        aliases: list[dict[str, str]]
        """

        default_class = Default

        def __init__(self, data=None):
            super().__init__()
            self.id = None
            self.name = None
            self.aliases = None
            self.description = None
            self.tracks = None
            self.genre = None
            self.status = None
            self.availability = None
            self.notes = None
            self.usageRights = None
            self.details = self.Details(None)

        class Details(dt.DataclassSub):
            """Contains details."""
            def __init__(self, datas: dict = None):
                super().__init__()
                self.avatarUrl = None
                self.bannerUrl = None
                self.socials = None

        def dict_from_default(self, data: Default):
            return {
                "id": data.vadb_info.artist_id,
                "name": data.name,
                "aliases": [{"name": alias.name} for alias in data.details.aliases],
                "description": data.details.description,
                "tracks": data.details.music_info.tracks,
                "genre": data.details.music_info.genre,
                "status": data.states.status.value,
                "availability": data.states.availability.value,
                "notes": data.details.notes,
                "usageRights": data.states.usage_rights,
                "details": {
                    "avatarUrl": data.details.images.avatar_url,
                    "bannerUrl": data.details.images.banner_url,
                    "socials": data.details.socials
                }
            }


class Firebase:
    """Contains classes for Firebase Interaction."""

    class Logging(dt.NonStandardDataclass, ArtistStructure):
        """Class for logging and receiving pending and editing artists."""

        default_class = Default

        def __init__(self, data=None):
            super().__init__()
            self.artist_id = None
            self.data: Default = None

        def dict_from_default(self, data: Default):
            return {
                    "artist_id": data.vadb_info.artist_id,
                    "data": data
                }

        def send_data(self, log_type: l_l.LogTypes.Pending | l_l.LogTypes.Editing):
            """Sends the data to Firebase."""
            f_i.edit_data(log_type.path, {self.artist_id: self.data.get_dict()})



def search_for_artist(search_term: str) -> list[Default]:
    """Searches for artists on VADB."""

    search_term_url = ul.quote_plus(search_term)
    search_term_url = search_term_url.replace("+", "%20")
    try:
        response = v_i.make_request("GET", f"/search/{search_term_url}")
    except req.exceptions.HTTPError:
        return None

    artists_data = response["data"]
    artist_list = [Default(VADB.Receive(artist_data)) for artist_data in artists_data]

    return artist_list

def check_if_has_entry_firebase(artist_id: int):
    """Checks if there's an entry in Firebase."""
    for other in ("pending", "editing"):
        if f_i.is_data_exists(["artistData", other, "data", artist_id]):
            return True

    return False

def generate_search_embed(result: list[Default]):
    """Returns an embed for searches with multiple results."""

    embed = nx.Embed(color=0xFF0000)

    str_list = []
    for artist in result:
        artist_id = artist.vadb_info.artist_id
        if artist_id is None:
            artist_id = "(Unknown ID)"
        str_list.append(f"**{artist_id}**: {artist.name}")

    value_string = "\n".join(str_list)

    embed.add_field(name=(
        "Multiple artists found!\n"
        "`<ID>: <Artist Name>`"
        ), value=value_string)

    return embed

def get_artist_by_id_vadb(artist_id: int):
    """Gets an artist from VADB by ID."""
    artist = Default(VADB.Receive(v_i.make_request("GET", f"/artist/{artist_id}")["data"]))
    return artist

def get_artist_by_id_fb(log_type: l_l.LogTypes.Pending | l_l.LogTypes.Editing, artist_id: int):
    """Gets an artist from Firebase by ID and log type."""
    diction = f_i.get_data(log_type.path + [str(artist_id)])
    artist = Default()
    artist.from_dict(diction)
    return artist

def create_log_list(logs):
    """Creates a list of log objects."""
    return [l_l.Log().from_dict(log) for log in logs] if logs is not None else None
