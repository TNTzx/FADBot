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
from typing import Union
import urllib.parse as ul
import discord
from discord.enums import DefaultAvatar
import discord.ext.commands as cmds

import tldextract as tld

from global_vars import variables as vrs
from functions.artist_related import asking as ask
from functions.exceptions import custom_exc as c_exc
from functions import other_functions as o_f


DEFAULT_IMAGE = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"

class ArtistDataStructure():
    """Defines a common data structure for artists."""

    def get_default_dict(self):
        """Gets the default dictionary."""
        return self.__class__(Structures.Default()).to_dict()

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


class Structures:
    """Contains classes for artist data structures."""

    class Default(ArtistDataStructure):
        """Main artist data structure. Must initiate first.
        name: str
        proof: str
        vadb_info: VADBInfo
        states: States
        details: Details
        """

        default = {
            "name": "",
            "proof": None,
            "vadb_info": {
                "artist_id": None,
                "page": "https://fadb.live/"
            },
            "states": {
                "status": 2,
                "availability": 2,
                "usage_rights": [{}]
            },
            "details": {
                "description": "",
                "notes": "",
                "aliases": [{}],
                "images": {
                    "avatar_url": None,
                    "banner_url": None
                },
                "music_info": {
                    "tracks": 0,
                    "genre": "Mixed"
                },
                "socials": [{}]
            }
        }

        def __init__(self,
                datas: Union[
                    dict,
                    Structures.VADB.Send.Create,
                    Structures.VADB.Send.Edit,
                    Structures.VADB.Receive
                ] = None):

            if isinstance(datas, dict):
                datas = o_f.override_dicts_recursive(Structures.Default.default, datas)
            elif datas is None:
                datas = Structures.Default.default
            else:
                if isinstance(datas, Structures.VADB.Send.Create):
                    datas = {
                        "name": datas.name,
                        "states": {
                            "status": datas.status,
                            "availability": datas.availability
                        }
                    }
                elif isinstance(datas, Structures.VADB.Send.Edit):
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
                elif isinstance(datas, Structures.VADB.Receive):
                    datas = {
                        "vadb_info": {
                            "artist_id": datas.id,
                            "page": datas.name
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
                datas = o_f.override_dicts_recursive(Structures.Default.default, datas)


            self.name = datas["name"]
            self.proof = datas["proof"]
            self.vadb_info = self.VADBInfo(datas["vadb_info"])
            self.states = self.States(datas["states"])
            self.details = self.Details(datas["details"])

        class VADBInfo:
            """Stores VADB-Related info.
            artist_id: int
            page: str
            """
            def __init__(self, datas: dict = None):
                self.artist_id = datas["artist_id"]
                self.page = datas["page"]

        class States:
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

        class Details:
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
                self.images = self.Images(datas["images"])
                self.music_info = self.MusicInfo(datas["music_info"])
                self.socials = datas["socials"]

            class Images:
                """Stores the images of the artist.
                avatar_url: str
                banner_url: str
                """
                def __init__(self, datas: dict = None):
                    self.avatar_url = datas["avatar_url"]
                    self.banner_url = datas["banner_url"]

            class MusicInfo:
                """Stores the information about the artist's music.
                tracks: int
                genre: str
                """
                def __init__(self, datas: dict = None):
                    self.tracks = datas["tracks"]
                    self.genre = datas["genre"]

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

        async def set_attribute(self, attr: o_f.Unique, ctx, skippable):
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
                    skippable=skippable
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
                    skippable=skippable
                )
                if description is not None:
                    self.details.description = description
            elif check(functions.notes):
                notes = await ask.wait_for_response(ctx,
                    "Notes",
                    "Send other notes you want to put in.",
                    ask.OutputTypes.text,
                    skippable=skippable
                )
                if notes is not None:
                    self.details.notes = notes
            elif check(functions.aliases):
                aliases = await ask.wait_for_response(ctx,
                    "Artist Aliases",
                    "Send other names that the artist goes by.",
                    ask.OutputTypes.listing,
                    skippable=skippable
                )
                if aliases is not None:
                    self.details.aliases = [{"name": alias} for alias in aliases]
            elif check(functions.avatar_url):
                avatar_url = await ask.wait_for_response(ctx,
                    "Send an image to an avatar of the artist.",
                    "This is the profile picture that the artist uses.",
                    ask.OutputTypes.image,
                    skippable=skippable
                )
                if avatar_url is not None:
                    self.details.images.avatar_url = avatar_url
            elif check(functions.banner_url):
                banner = await ask.wait_for_response(ctx,
                    "Send an image to the banner of the artist.",
                    "This is the banner that the artist uses.",
                    ask.OutputTypes.image,
                    skippable=skippable
                )
                if banner is not None:
                    self.details.images.banner_url = banner
            elif check(functions.tracks):
                tracks = await ask.wait_for_response(ctx,
                    "How many tracks does the artist have?",
                    "This is the count for how much music the artist has produced. It can easily be found on Soundcloud pages, if you were wondering.",
                    ask.OutputTypes.number,
                    skippable=skippable
                )
                if tracks is not None:
                    self.details.music_info.tracks = tracks
            elif check(functions.genre):
                genre = await ask.wait_for_response(ctx,
                    "What is the genre of the artist?",
                    "This is the type of music that the artist makes.",
                    ask.OutputTypes.text,
                    skippable=skippable
                )
                if genre is not None:
                    self.details.music_info.genre = genre
            elif check(functions.socials):
                socials = await ask.wait_for_response(ctx,
                    "Put some links for the artist's social media here.",
                    "This is where you put in links for the artist's socials such as Youtube, Spotify, Bandcamp, etc.",
                    ask.OutputTypes.links,
                    skippable=skippable
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
                    "avatar": functions.avatar_url,
                    "banner": functions.banner_url,
                    "tracks": functions.tracks,
                    "genre": functions.genre,
                    "usagerights": functions.usage_rights,
                    "socials": functions.socials,
                    "notes": functions.notes
                }

            while True:
                await ctx.author.send(f"This is the generated artist profile.\nUse `{vrs.CMD_PREFIX}edit <property>` to edit a property, `{vrs.CMD_PREFIX}submit` to submit this verification for approval, or `{vrs.CMD_PREFIX}cancel` to cancel this command.")

                await ctx.author.send(embed=await self.generate_embed(editing=True))

                message: discord.Message = await ask.waiting(ctx)
                command = message.content.split(" ")

                if command[0].startswith(f"{vrs.CMD_PREFIX}edit"):
                    command_to_get = command_dict.get(command[1] if len(command) > 1 else None, None)

                    if command_to_get is None:
                        await ask.send_error(ctx, f"You didn't specify a valid property! The valid properties are `{'`, `'.join(command_dict.keys())}`")
                        continue

                    await command_to_get(ctx, skippable=True)

                elif command[0] == f"{vrs.CMD_PREFIX}submit":
                    break

                elif command[0] == f"{vrs.CMD_PREFIX}cancel":
                    raise c_exc.ExitFunction("Exited Function.")

                else:
                    await ask.send_error(ctx, "You didn't send a command!")

        async def generate_embed(self, editing=False):
            """Generates an embed."""

            embed = discord.Embed()
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
            alias_list = [alias['name'] for alias in aliases]
            aliases = f"`{'`, `'.join(alias_list)}`" if len(alias_list) > 0 else "No aliases!"
            embed.add_field(name=f"Aliases{edit_format('aliases')}:", value=self.details.aliases)


            description = self.details.description
            description = description if description is not None else "No description!"
            embed.add_field(name=f"Description{edit_format('description')}:", value=description, inline=False)

            vadb_page = self.vadb_info.page
            vadb_page = f"[Click here!]({vadb_page})" if vadb_page is not None else "Not submitted yet!"
            embed.add_field(name="VADB Page:", value=vadb_page, inline=False)


            status = self.states.status.get_name()
            status = f"**__{status}__**"
            embed.add_field(name="Status:", value=status)

            availability = self.states.availability.get_name()
            availability = f"**__{availability}__**"
            embed.add_field(name=f"Availability{edit_format('availability')}:", value=availability, inline=False)

            usage_rights = self.states.usage_rights
            if len(usage_rights) > 0:
                usage_list = []
                for entry in usage_rights:
                    status_rights = entry["value"]
                    usage_list.append(f"{entry['name']}: {'Verified' if status_rights else 'Disallowed'}")
                usage_rights = "\n".join(usage_list)
            else:
                usage_rights = f"All songs: {availability}"
            embed.add_field(name=f"Specific usage rights{edit_format('usageRights')}:", value=f"`{usage_rights}`")


            socials = self.details.socials
            if len(socials) > 0:
                socials_list = []
                for entry in socials:
                    link, domain = entry["link"], entry["type"]
                    socials_list.append(f"[{domain}]({link})")
                socials = " ".join(socials_list)
            else:
                socials = "No socials links!"
            embed.add_field(name=f"Social links{edit_format('socials')}:", value=socials, inline=False)

            notes = self.details.notes
            notes = notes if notes is not None else "No other notes!"
            embed.add_field(name=f"Other notes{edit_format('notes')}:", value=notes)


            color_keys = {
                "green": 0x00FF00,
                "red": 0xFF0000,
                "yellow": 0xFFFF00,
                "blue": 0x0000FF
            }
            color_match = o_f.Match(color_keys, "green")

            if status == "Completed":
                if availability == "Verified":
                    color_match.value = "green"
                elif availability == "Disallowed":
                    color_match.value = "red"
                elif availability == "Contact Required":
                    color_match.value = "yellow"
                elif availability == "Varies":
                    color_match.value = "blue"
            elif status in ["No Contact", "Pending"]:
                color_match.value = "yellow"

            embed.colour = color_match.get_name()

            return embed


    class VADB:
        """Contains classes for VADB Interaction."""

        class Send:
            """Contains classes for sending data to VADB's API."""

            class Create(ArtistDataStructure):
                """Data structure for sending the "create artist" request.
                name: str
                status: int
                availability: int"""

                def __init__(self, datas: Union[dict, Structures.Default] = None):
                    if isinstance(datas, Structures.Default):
                        datas = {
                            "name": datas.name,
                            "status": datas.states.status.value,
                            "availability": datas.states.availability.value
                        }
                    elif isinstance(datas, dict):
                        print(self.get_default_dict())
                        datas = o_f.override_dicts_recursive(self.get_default_dict(), datas)
                    else:
                        datas = self.get_default_dict()

                    self.name = datas["name"]
                    self.status = datas["status"]
                    self.availability = datas["availability"]

            class Edit(ArtistDataStructure):
                """Data structure for sending the "edit artist" request."""

                def __init__(self, datas: Union[dict, Structures.Default] = None):
                    if isinstance(datas, Structures.Default):
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



        class Receive(ArtistDataStructure):
            """Data structure for a received response from VADB's API.
            id: int
            name: str
            aliases: list[dict[str, str]]
            """
            def __init__(self, datas: Union[dict, Structures.Default] = None):
                if isinstance(datas, Structures.Default):
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

            class Details:
                """Contains details."""
                def __init__(self, datas: dict = None):
                    self.avatarUrl = datas["avatarUrl"]
                    self.bannerUrl = datas["bannerUrl"]
                    self.socials = datas["socials"]
