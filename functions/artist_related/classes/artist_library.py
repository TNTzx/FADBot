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
from os import path
import urllib.parse as ul
import abc
from nextcord import channel
from nextcord import message
from nextcord.message import Message
import requests as req
import nextcord as nx
import nextcord.ext.commands as cmds

import tldextract as tld

from global_vars import variables as vrs
from functions.artist_related import asking as ask
from functions.databases.firebase import firebase_interaction as f_i
from functions.databases.vadb import vadb_interact as v_i
from functions.exceptions import custom_exc as c_exc
from functions import other_functions as o_f


DEFAULT_IMAGE = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"

class ArtistDataStructure():
    """Defines a common data structure for artists."""

    def get_default_dict(self):
        """Gets the default dictionary."""
        return self.__class__(ArtistStructures.Default()).to_dict()

    def to_dict(self):
        """Turns the data into a dictionary."""
        return o_f.get_dict_attr(self)

    def get_json_dict(self):
        """Turns the data into a dictionary for sending."""
        data: dict = self.to_dict()
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = str(value)

        return data

class ArtistDataSubStructure():
    """Defines a structure for nested classes inside an ArtistDataStructure."""


def check_if_empty(variable):
    """Returns the variable if it is not None or not an empty iterable."""
    if variable is not None:
        if len(variable) == 0:
            return None
    return variable


class ArtistStructures:
    """Contains classes for artist data structures."""

    class Default(ArtistDataStructure):
        """Main artist data structure. Must initiate first.
        name: str
        proof: str
        vadb_info: VADBInfo
        states: States
        details: Details
        """

        DEFAULT = {
            "name": "default name",
            "proof": DEFAULT_IMAGE,
            "vadb_info": {
                "artist_id": None,
                "page": "https://fadb.live/"
            },
            "discord_info": {
                "logs": None
            },
            "states": {
                "status": 2,
                "availability": 2,
                "usage_rights": None
            },
            "details": {
                "description": None,
                "notes": None,
                "aliases": None,
                "images": {
                    "avatar_url": DEFAULT_IMAGE,
                    "banner_url": DEFAULT_IMAGE
                },
                "music_info": {
                    "tracks": 0,
                    "genre": None
                },
                "socials": None
            }
        }

        def __init__(self,
                datas: dict | ArtistStructures.VADB.Send.Create | ArtistStructures.VADB.Send.Edit | ArtistStructures.VADB.Receive | ArtistStructures.Firebase.Send = None):

            if isinstance(datas, dict):
                datas = o_f.override_dicts_recursive(ArtistStructures.Default.DEFAULT, datas)
            elif datas is None:
                datas = ArtistStructures.Default.DEFAULT
            else:
                if isinstance(datas, ArtistStructures.VADB.Send.Create):
                    datas = {
                        "name": datas.name,
                        "states": {
                            "status": datas.status,
                            "availability": datas.availability
                        }
                    }
                elif isinstance(datas, ArtistStructures.VADB.Send.Edit):
                    datas = {
                        "name": datas.name,
                        "states": {
                            "status": datas.status,
                            "availability": datas.availability,
                            "usage_rights": datas.usageRights
                        },
                        "details": {
                            "description": datas.description,
                            "notes": datas.notes,
                            "aliases": datas.aliases,
                            "images": {
                                "avatar_url": datas.avatarUrl,
                                "banner_url": datas.bannerUrl
                            },
                            "music_info": {
                                "tracks": datas.tracks,
                                "genre": datas.genre
                            },
                            "socials": datas.socials
                        }
                    }
                elif isinstance(datas, ArtistStructures.VADB.Receive):
                    datas = {
                        "name": datas.name,
                        "vadb_info": {
                            "artist_id": datas.id,
                            "page": f"https://fadb.live/artist/{datas.id}"
                        },
                        "states": {
                            "status": datas.status,
                            "availability": datas.availability,
                            "usage_rights": datas.usageRights
                        },
                        "details": {
                            "description": datas.description,
                            "notes": datas.notes,
                            "aliases": datas.aliases,
                            "images": {
                                "avatar_url": datas.details.avatarUrl,
                                "banner_url": datas.details.bannerUrl
                            },
                            "music_info": {
                                "tracks": datas.tracks,
                                "genre": datas.genre
                            },
                            "socials": datas.details.socials
                        }
                    }
                elif isinstance(datas, ArtistStructures.Firebase.Send):
                    datas = {
                        "name": datas.name,
                        "vadb_info": {
                            "artist_id": datas.artist_id
                        },
                        "discord_info": {
                            "logs": datas.logs
                        }
                    }
                datas = o_f.override_dicts_recursive(ArtistStructures.Default.DEFAULT, datas)


            self.name = datas["name"]
            self.proof = datas["proof"]
            self.vadb_info = self.VADBInfo(datas["vadb_info"])
            self.discord_info = self.DiscordInfo(datas["discord_info"])
            self.states = self.States(datas["states"])
            self.details = self.Details(datas["details"])

        class VADBInfo(ArtistDataSubStructure):
            """Stores VADB-Related info.
            artist_id: int
            page: str
            """
            def __init__(self, datas: dict = None):
                self.artist_id = datas["artist_id"]
                self.page = datas["page"]

        class DiscordInfo(ArtistDataStructure):
            """Stores Discord-related info.
            logs: list[dict[str, int]]"""

            def __init__(self, datas):
                self.logs = datas["logs"]

        class States(ArtistDataSubStructure):
            """Stores the state of the artist in the verification process.\n
            status: int
            availability: int
            usage_rights: list[dict[str, Any]]
            """
            def __init__(self, datas: dict = None):
                status_dict = {
                    0: "Completed",
                    1: "No Contact",
                    2: "Pending",
                    3: "Requested"
                }
                self.status: o_f.Match = o_f.Match(status_dict, datas["status"])

                availability_dict = {
                    0: "Verified",
                    1: "Disallowed",
                    2: "Contact Required",
                    3: "Varies"
                }
                self.availability: o_f.Match = o_f.Match(availability_dict, datas["availability"])

                self.usage_rights: list[dict[str, str]] = datas["usage_rights"]
                self.usage_rights = check_if_empty(self.usage_rights)

        class Details(ArtistDataSubStructure):
            """Stores details of the artist.
            description: str
            notes: str
            aliases: list[dict[str, str]]
            images: Images
            music_info: MusicInfo
            socials: list[dict[str, Any]]
            """
            def __init__(self, datas: dict = None):
                self.description = datas["description"]
                self.notes = datas["notes"]
                self.aliases = datas["aliases"]
                self.aliases = check_if_empty(self.aliases)
                self.images = self.Images(datas["images"])
                self.music_info = self.MusicInfo(datas["music_info"])
                self.socials = datas["socials"]
                self.socials = check_if_empty(self.socials)

            class Images(ArtistDataSubStructure):
                """Stores the images of the artist.
                avatar_url: str
                banner_url: str
                """
                def __init__(self, datas: dict = None):
                    self.avatar_url = datas["avatar_url"]
                    self.banner_url = datas["banner_url"]

            class MusicInfo(ArtistDataSubStructure):
                """Stores the information about the artist's music.
                tracks: int
                genre: str
                """
                def __init__(self, datas: dict = None):
                    self.tracks = datas["tracks"]
                    self.genre = datas["genre"]

        async def generate_embed(self, editing=False):
            """Generates an embed."""

            embed = nx.Embed()
            embed.title = f"Artist data for {self.name}:"
            embed.description = "_ _"

            def edit_format(prefix):
                return f" (`{vrs.CMD_PREFIX}edit {prefix}`)" if editing else ""

            id_format = self.vadb_info.artist_id if self.vadb_info.artist_id is not None else "Not submitted yet!"

            embed.set_author(
                name=f"{self.name} (ID: {id_format})",
                url=self.vadb_info.page,
                icon_url=self.details.images.avatar_url
            )

            embed.set_thumbnail(url=self.details.images.avatar_url)
            embed.set_image(url=self.details.images.banner_url)

            embed.add_field(name=f"Name{edit_format('name')}:", value=f"**{self.name}**")


            aliases = self.details.aliases
            if aliases is not None:
                alias_list = [alias['name'] for alias in aliases]
                aliases = f"`{'`, `'.join(alias_list)}`"
            else:
                aliases = "No aliases!"
            embed.add_field(name=f"Aliases{edit_format('aliases')}:", value=aliases)


            description = self.details.description
            description = description if o_f.is_not_blank_str(description) else "No description!"
            embed.add_field(name=f"Description{edit_format('description')}:", value=description, inline=False)

            vadb_page = self.vadb_info.page
            vadb_page = f"[Click here!]({vadb_page})" if not (vadb_page == ArtistStructures.Default.DEFAULT["vadb_info"]["page"]) and o_f.is_not_blank_str(vadb_page) else "Not submitted yet!"
            embed.add_field(name="VADB Page:", value=vadb_page, inline=False)


            status = self.states.status.get_name()
            status = f"**__{status}__**"
            embed.add_field(name="Status:", value=status, inline=False)

            availability = self.states.availability.get_name()
            availability = f"**__{availability}__**"
            embed.add_field(name=f"Availability{edit_format('availability')}:", value=availability)

            usage_rights = self.states.usage_rights
            if usage_rights is not None:
                usage_list = []
                for entry in usage_rights:
                    status_rights = entry["value"]
                    usage_list.append(f"{entry['name']}: {'Verified' if status_rights else 'Disallowed'}")
                usage_rights = "\n".join(usage_list)
            else:
                usage_rights = "No other specific usage rights!"
            embed.add_field(name=f"Specific usage rights{edit_format('usageRights')}:", value=f"`{usage_rights}`")


            socials = self.details.socials
            if socials is not None:
                socials_list = []
                for entry in socials:
                    link_type: str = entry["type"]
                    link_type = link_type.capitalize()
                    link = entry["link"]
                    socials_list.append(f"[{link_type}]({link})")
                socials = " ".join(socials_list)
            else:
                socials = "No socials links!"
            embed.add_field(name=f"Social links{edit_format('socials')}:", value=socials, inline=False)

            notes = self.details.notes
            notes = notes if o_f.is_not_blank_str(notes) else "No other notes!"
            embed.add_field(name=f"Other notes{edit_format('notes')}:", value=notes)

            if editing:
                embed.add_field(name=f"{edit_format('avatar_url')} for editing the avatar\n{edit_format('banner_url')} for editing the banner", value="_ _", inline=False)


            color_keys = {
                "green": 0x00FF00,
                "red": 0xFF0000,
                "yellow": 0xFFFF00,
                "blue": 0x0000FF
            }
            color_match = o_f.Match(color_keys, "green")

            if self.states.status.value == 0: # completed
                if self.states.availability.value == 0: # verified
                    color_match.value = "green"
                elif self.states.availability.value == 1: # disallowed
                    color_match.value = "red"
                elif self.states.availability.value == 2: # contact required
                    color_match.value = "yellow"
                elif self.states.availability.value == 3: # varies
                    color_match.value = "blue"
            elif self.states.status.value in (1, 2): # no contact / pending
                color_match.value = "yellow"

            embed.colour = color_match.get_name()

            return embed


        class Functions:
            """Contains identifiers for the set_attribute() function."""
            name = o_f.Unique()
            proof = o_f.Unique()
            availability = o_f.Unique()
            usage_rights = o_f.Unique()
            description = o_f.Unique()
            notes = o_f.Unique()
            aliases = o_f.Unique()
            avatar_url = o_f.Unique()
            banner_url = o_f.Unique()
            tracks = o_f.Unique()
            genre = o_f.Unique()
            socials = o_f.Unique()

        async def set_attribute(self, ctx: cmds.Context, attr: o_f.Unique, skippable=False):
            """Sets an attribute in this class."""
            functions = self.Functions

            def check(attrib):
                return attr == attrib

            if check(functions.name):
                name = await ask.wait_for_response(ctx,
                    "Artist Name",
                    "Send the artist name.",
                    ask.OutputTypes.text,
                    skippable=skippable
                )

                search_result = search_for_artist(name)
                if search_result is not None:
                    await ctx.author.send("Other artist(s) found. Please check if you have a duplicate submission.\nUse `##cancel` if you think you have a different artist, or type anything to continue.", embed=generate_search_embed(search_result))
                    response = await ask.waiting(ctx)
                    response = await ask.reformat(ctx, ask.OutputTypes.text, response)

                    if response == "##cancel":
                        return

                if name is not None:
                    self.name = name

            elif check(functions.proof):
                proof = await ask.wait_for_response(ctx,
                    "Please send proof that you contacted the artist.",
                    "Take a screenshot of the email/message that the artist sent you that proves the artist's verification/unverification. You can only upload 1 image/link.",
                    ask.OutputTypes.image,
                    skippable=skippable
                )
                if proof is not None:
                    self.proof = proof
            elif check(functions.availability):
                availability = await ask.wait_for_response(ctx,
                    "Is the artist verified, disallowed, or does it vary between songs?",
                    "\"Verified\" means that the artist's songs are allowed to be used for custom PA levels.\n\"Disallowed\" means that the artist's songs cannot be used.\n\"Varies\" means that it depends per song, for example, remixes aren't allowed for use but all their other songs are allowed.",
                    ask.OutputTypes.text, choices=["Verified", "Disallowed", "Varies"],
                    skippable=skippable
                )
                if availability is not None:
                    dictionary = {
                        "verified": 0,
                        "disallowed": 1,
                        "varies": 3,
                    }
                    self.states.availability.value = dictionary[availability]
            elif check(functions.usage_rights):
                usage_rights = await ask.wait_for_response(ctx,
                    "What are the usage rights for the artist?",
                    "This is where you put in the usage rights. For example, if remixes aren't allowed, you can type in `\"Remixes: Disallowed\"`. Add more items as needed.",
                    ask.OutputTypes.dictionary, choices_dict=["Verified", "Disallowed"],
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
            elif check(functions.description):
                description = await ask.wait_for_response(ctx,
                    "Send a description about the artist.",
                    "You can put information about the artist here. Their bio, how their music is created, etc. could work.",
                    ask.OutputTypes.text,
                    skippable=True
                )
                if description is not None:
                    self.details.description = description
            elif check(functions.notes):
                notes = await ask.wait_for_response(ctx,
                    "Notes",
                    "Send other notes you want to put in.",
                    ask.OutputTypes.text,
                    skippable=True
                )
                if notes is not None:
                    self.details.notes = notes
            elif check(functions.aliases):
                aliases = await ask.wait_for_response(ctx,
                    "Artist Aliases",
                    "Send other names that the artist goes by.",
                    ask.OutputTypes.listing,
                    skippable=True
                )
                if aliases is not None:
                    self.details.aliases = [{"name": alias} for alias in aliases]
            elif check(functions.avatar_url):
                avatar_url = await ask.wait_for_response(ctx,
                    "Send an image to an avatar of the artist.",
                    "This is the profile picture that the artist uses.",
                    ask.OutputTypes.image,
                    skippable=True
                )
                if avatar_url is not None:
                    self.details.images.avatar_url = avatar_url
            elif check(functions.banner_url):
                banner = await ask.wait_for_response(ctx,
                    "Send an image to the banner of the artist.",
                    "This is the banner that the artist uses.",
                    ask.OutputTypes.image,
                    skippable=True
                )
                if banner is not None:
                    self.details.images.banner_url = banner
            elif check(functions.tracks):
                tracks = await ask.wait_for_response(ctx,
                    "How many tracks does the artist have?",
                    "This is the count for how much music the artist has produced. It can easily be found on Soundcloud pages, if you were wondering.",
                    ask.OutputTypes.number,
                    skippable=True
                )
                if tracks is not None:
                    self.details.music_info.tracks = tracks
            elif check(functions.genre):
                genre = await ask.wait_for_response(ctx,
                    "What is the genre of the artist?",
                    "This is the type of music that the artist makes.",
                    ask.OutputTypes.text,
                    skippable=True
                )
                if genre is not None:
                    self.details.music_info.genre = genre
            elif check(functions.socials):
                socials = await ask.wait_for_response(ctx,
                    "Put some links for the artist's social media here.",
                    "This is where you put in links for the artist's socials such as Youtube, Spotify, Bandcamp, etc.",
                    ask.OutputTypes.links,
                    skippable=True
                )
                social_list = []
                if socials is not None:
                    for link in socials:
                        type_link: str = tld.extract(link).domain
                        type_link = type_link.capitalize()
                        social_list.append({
                            "link": link,
                            "type": type_link
                        })
                    self.details.socials = social_list

        async def edit_loop(self, ctx: cmds.Context):
            """Initiates an edit loop to edit the attributes."""
            functions = self.Functions
            command_dict = {
                    "proof": functions.proof,
                    "availability": functions.availability,
                    "name": functions.name,
                    "aliases": functions.aliases,
                    "description": functions.description,
                    "avatar_url": functions.avatar_url,
                    "banner_url": functions.banner_url,
                    "tracks": functions.tracks,
                    "genre": functions.genre,
                    "usagerights": functions.usage_rights,
                    "socials": functions.socials,
                    "notes": functions.notes
                }

            while True:
                await ctx.author.send(f"This is the generated artist profile.\nUse `{vrs.CMD_PREFIX}edit <property>` to edit a property, `{vrs.CMD_PREFIX}submit` to submit this verification for approval, or `{vrs.CMD_PREFIX}cancel` to cancel this command.")

                await ctx.author.send(embed=await self.generate_embed(editing=True))

                message_obj: nx.Message = await ask.waiting(ctx)
                command = message_obj.content.split(" ")

                if command[0].startswith(f"{vrs.CMD_PREFIX}edit"):
                    command_to_get = command_dict.get(command[1] if len(command) > 1 else None, None)

                    if command_to_get is None:
                        await ask.send_error(ctx, f"You didn't specify a valid property! The valid properties are `{'`, `'.join(command_dict.keys())}`")
                        continue

                    await self.set_attribute(ctx, command_to_get, skippable=True)

                elif command[0] == f"{vrs.CMD_PREFIX}submit":
                    break

                elif command[0] == f"{vrs.CMD_PREFIX}cancel":
                    raise c_exc.ExitFunction("Exited Function.")

                else:
                    await ask.send_error(ctx, "You didn't send a command!")

        async def trigger_all_set_attributes(self, ctx: cmds.Context):
            """Triggers all attributes."""
            async def trigger(cmd):
                await self.set_attribute(ctx, cmd)

            await trigger(self.Functions.name)
            # add check for existing artist here
            await trigger(self.Functions.proof)
            await trigger(self.Functions.availability)
            await trigger(self.Functions.usage_rights)
            await trigger(self.Functions.aliases)
            await trigger(self.Functions.description)
            await trigger(self.Functions.avatar_url)
            await trigger(self.Functions.banner_url)
            await trigger(self.Functions.tracks)
            await trigger(self.Functions.genre)
            await trigger(self.Functions.socials)
            await trigger(self.Functions.notes)


        async def post_log(self, _type: o_f.Unique):
            """Posts logs to everyone."""
            await LogStructures.Dump(self).post_logs_discord(_type)
            await LogStructures.Live(self).post_logs_discord(_type)



    class VADB:
        """Contains classes for VADB Interaction."""

        class Send:
            """Contains classes for sending data to VADB's API."""

            class Create(ArtistDataStructure):
                """Data structure for sending the "create artist" request.
                name: str
                status: int
                availability: int"""

                def __init__(self, datas: dict | ArtistStructures.Default = None):
                    if isinstance(datas, ArtistStructures.Default):
                        datas = {
                            "name": datas.name,
                            "status": datas.states.status.value,
                            "availability": datas.states.availability.value
                        }
                    elif isinstance(datas, dict):
                        datas = o_f.override_dicts_recursive(self.get_default_dict(), datas)
                    else:
                        datas = self.get_default_dict()

                    self.name = datas["name"]
                    self.status = datas["status"]
                    self.availability = datas["availability"]

                def send_data(self):
                    """Creates the artist using the current instance."""
                    return v_i.make_request("POST", "/artist/", self.get_json_dict())

            class Edit(ArtistDataStructure):
                """Data structure for sending the "edit artist" request."""

                def __init__(self, datas: dict | ArtistStructures.Default = None):
                    if isinstance(datas, ArtistStructures.Default):
                        datas = {
                            "name": datas.name,

                            "status": datas.states.status.value,
                            "availability": datas.states.availability.value,
                            "usageRights": datas.states.usage_rights,

                            "aliases": datas.details.aliases,
                            "description": datas.details.description,
                            "notes": datas.details.notes,
                            "tracks": datas.details.music_info.tracks,
                            "genre": datas.details.music_info.genre,
                            "avatarUrl": datas.details.images.avatar_url,
                            "bannerUrl": datas.details.images.banner_url,
                            "socials": datas.details.socials
                        }
                    elif isinstance(datas, dict):
                        datas = o_f.override_dicts_recursive(self.get_default_dict(), datas)
                    else:
                        datas = self.get_default_dict()

                    self.name = datas["name"]
                    self.status = datas["status"]
                    self.availability = datas["availability"]
                    self.usageRights = datas["usageRights"]
                    self.aliases = datas["aliases"]
                    self.description = datas["description"]
                    self.notes = datas["notes"]
                    self.tracks = datas["tracks"]
                    self.genre = datas["genre"]
                    self.avatarUrl = datas["avatarUrl"]
                    self.bannerUrl = datas["bannerUrl"]
                    self.socials = datas["socials"]

                def send_data(self, artist_id):
                    """Edits the artist using the current instance."""
                    return v_i.make_request("PATCH", f"/artist/{artist_id}", self.get_json_dict())

            class Delete(ArtistDataStructure):
                """Data structure for requesting to completely obliterate the artist from the database.
                id: int"""

                def __init__(self, datas: dict | ArtistStructures.Default = None):
                    if isinstance(datas, ArtistStructures.Default):
                        datas = {
                            "id": datas.vadb_info.artist_id
                        }
                    elif isinstance(datas, dict):
                        datas = o_f.override_dicts_recursive(self.get_default_dict(), datas)
                    else:
                        datas = self.get_default_dict()

                    self.artist_id = datas["id"]

                def send_data(self):
                    """Completely obliterates the artist from the database."""
                    return v_i.make_request("DELETE", f"/artist/{self.artist_id}")

        class Receive(ArtistDataStructure):
            """Data structure for a received response from VADB's API.
            id: int
            name: str
            aliases: list[dict[str, str]]
            """
            def __init__(self, datas: dict | ArtistStructures.Default = None):
                if isinstance(datas, ArtistStructures.Default):
                    datas = {
                        "id": datas.vadb_info.artist_id,
                        "name": datas.name,
                        "aliases": datas.details.aliases,
                        "description": datas.details.description,
                        "tracks": datas.details.music_info.tracks,
                        "genre": datas.details.music_info.genre,
                        "status": datas.states.status.value,
                        "availability": datas.states.availability.value,
                        "notes": datas.details.notes,
                        "usageRights": datas.states.usage_rights,
                        "details": {
                            "avatarUrl": datas.details.images.avatar_url,
                            "bannerUrl": datas.details.images.banner_url,
                            "socials": datas.details.socials
                        }
                    }
                elif isinstance(datas, dict):
                    datas = o_f.override_dicts_recursive(self.get_default_dict(), datas)
                else:
                    datas = self.get_default_dict()


                self.id = datas["id"]
                self.name = datas["name"]
                self.aliases = datas["aliases"]
                self.description = datas["description"]
                self.tracks = datas["tracks"]
                self.genre = datas["genre"]
                self.status = datas["status"]
                self.availability = datas["availability"]
                self.notes = datas["notes"]
                self.usageRights = datas["usageRights"]
                self.details = self.Details(datas["details"])

            class Details(ArtistDataSubStructure):
                """Contains details."""
                def __init__(self, datas: dict = None):
                    self.avatarUrl = datas["avatarUrl"]
                    self.bannerUrl = datas["bannerUrl"]
                    self.socials = datas["socials"]


    class Firebase:
        """Contains classes for Firebase Interaction."""

        class Send:
            """Class for sending pending and editing artists."""
            class Base(ArtistDataStructure):
                """Base data structure for sending requests to Firebase."""
                def __init__(self, datas: dict | ArtistStructures.Default = None):
                    if isinstance(datas, ArtistStructures.Default):
                        datas = {
                            "id": datas.vadb_info.artist_id,
                            "name": datas.name,
                            "logs": datas.discord_info.logs
                        }
                    elif isinstance(datas, dict):
                        datas = o_f.override_dicts_recursive(self.get_default_dict(), datas)
                    else:
                        datas = self.get_default_dict()

                    print(datas)

                    self.artist_id = datas["id"]
                    self.name = datas["name"]
                    self.logs = datas["logs"]

                def send_logs_base(self, paths: list[str]):
                    """Creates log data in Firebase."""
                    f_i.edit_data(paths, {self.artist_id: {"name": self.name, "logs": self.logs}})

                def send_logs(self):
                    """Send logs."""

            class Pending(Base):
                """Pending."""
                def send_logs(self):
                    return super().send_logs_base(["artistData", "pending", "data"])

            class Editing(Base):
                """Editing"""
                def send_logs(self):
                    return super().send_logs_base(["artistData", "editing", "data"])


class LogType:
    """Base class for defining logging structures."""
    def __init__(self, datas: ArtistStructures.Default):
        self.datas = datas

    class LogContainer:
        """Class that contains structure for logs."""
        class IDs:
            """Stores IDs."""
            def __init__(self):
                self.message_embed = self.MessageIDs()
                self.message_proof = self.MessageIDs()

            class MessageIDs:
                """Stores IDs that refer to a message."""
                def __init__(self, channel_id: int = None, message_id: int = None):
                    self.channel_id = str(channel_id)
                    self.message_id = str(message_id)

            def get_dict(self):
                """Gets dict."""
                return o_f.get_dict_attr(self)

        class Objects:
            """Stores channel and message objects."""
            def __init__(self, id_object: LogType.LogContainer.IDs | None):
                def get_message_from_ids(message_id_object: LogType.LogContainer.IDs.MessageIDs):
                    channel_obj: nx.TextChannel = vrs.global_bot.get_channel(int(message_id_object.channel_id))
                    return channel_obj.fetch_message(int(message_id_object.message_id))
                self.message_embed = get_message_from_ids(id_object.message_embed)
                self.message_proof = get_message_from_ids(id_object.message_proof)


    def get_channels(self, paths) -> list[nx.TextChannel]:
        """Get channels from firebase path.
        {"tag": "pa server", "channel": int}"""
        paths = f_i.get_data(paths)
        channels = []
        for entry in paths:
            try:
                channels.append(vrs.global_bot.get_channel(int(entry["channel"])))
            except TypeError:
                pass
        return channels

    def post_logs_firebase(self, _type: o_f.Unique):
        """Posts logs on discord then puts the message links on firebase."""
        if _type == self.LoggingTypes.PENDING:
            ArtistStructures.Firebase.Send.Pending(self.datas).send_logs()
        elif _type == self.LoggingTypes.EDITING:
            ArtistStructures.Firebase.Send.Editing(self.datas).send_logs()

    class LoggingTypes:
        """Class that contains logging types, like pending or editing."""
        PENDING = o_f.Unique()
        EDITING = o_f.Unique()

    async def post_logs_discord_base(self, _type: o_f.Unique, paths: list[str], post_to_firebase=False):
        """Post logs to discord."""
        if _type == self.LoggingTypes.PENDING:
            message_intro = "A new pending artist submission has been added. Here are the current details:"
        elif _type == self.LoggingTypes.EDITING:
            message_intro = "A new edit submission has been added. Here are the current details:"

        def store_message_id(message_obj: nx.Message):
            return LogType.LogContainer.IDs.MessageIDs(message_obj.channel.id, message_obj.id)

        messages: list[self.LogContainer] = []
        for channel_obj in self.get_channels(paths):
            log = self.LogContainer.IDs()
            log.message_embed = store_message_id(await channel_obj.send(message_intro, embed=await self.datas.generate_embed()))
            log.message_proof = store_message_id(await channel_obj.send(self.datas.proof))
            messages.append(log.get_dict())
        self.datas.discord_info.logs = messages

        if post_to_firebase:
            self.post_logs_firebase(_type)

    async def post_logs_discord(self, _type: o_f.Unique):
        """Inherited function."""

class LogStructures:
    """Contains log structures."""
    class Dump(LogType):
        """Type where messages aren't deleted."""
        async def post_logs_discord(self, _type: o_f.Unique):
            await self.post_logs_discord_base(_type, paths=["logData", "dump"])

    class Live(LogType):
        """Type where messages are deleted."""
        async def post_logs_discord(self, _type: o_f.Unique):
            await self.post_logs_discord_base(_type, paths=["logData", "live"], post_to_firebase=True)


def search_vadb(search_term: str):
    """Searches for artists on VADB."""

    search_term_url = ul.quote_plus(search_term)
    search_term_url = search_term_url.replace("+", "%20")
    try:
        response = v_i.make_request("GET", f"/search/{search_term_url}")
    except req.exceptions.HTTPError:
        return None

    artists_data = response["data"]
    final_list = [ArtistStructures.Default(ArtistStructures.VADB.Receive(artist_data)) for artist_data in artists_data]
    return final_list

def search_for_artist(search_term: str) -> list[ArtistStructures.Default] | None:
    """Searches for artists."""
    return search_vadb(search_term)

def generate_search_embed(result: list[ArtistStructures.Default]):
    """Returns an embed for searches with multiple results."""

    embed = nx.Embed(color=0xFF0000)

    str_list = []
    for artist in result:
        artist_id = artist.vadb_info.artist_id
        if artist_id is None:
            artist_id = "(Unknown ID)"
        str_list.append(f"**{artist_id}**: {artist.name}")

    value_string = "\n".join(str_list)

    embed.add_field(name="Multiple artists found!\n`<ID>: <Artist Name>`", value=value_string)

    return embed

def get_artist_by_id(artist_id: int):
    """Gets an artist from VADB by ID."""
    return ArtistStructures.Default(ArtistStructures.VADB.Receive(v_i.make_request("GET", f"/artist/{artist_id}")["data"]))
