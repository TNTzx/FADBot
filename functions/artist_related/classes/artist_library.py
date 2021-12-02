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
import requests as req
import nextcord as nx
import nextcord.ext.commands as cmds

import tldextract as tld

import global_vars.variables as vrs
import functions.artist_related.asking as ask
import functions.artist_related.classes.log_library as l_l
import functions.databases.firebase.firebase_interaction as f_i
import functions.databases.vadb.vadb_interact as v_i
import functions.exceptions.custom_exc as c_exc
import functions.other_functions as o_f


DEFAULT_IMAGE = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"

class ArtistDataStructure(o_f.DataStructure):
    """Defines a common data structure for artists."""

    def get_default_dict(self):
        """Gets the default dictionary."""
        return self.__class__(ArtistStructures.Default()).get_dict()

    def get_json_dict(self):
        """Turns the data into a dictionary for sending."""
        data: dict = self.get_dict()
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = str(value)

        return data


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
                "logs": {
                    "pending": None,
                    "editing": None
                }
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
                datas: dict | ArtistStructures.VADB.Send.Create | ArtistStructures.VADB.Send.Edit | ArtistStructures.VADB.Receive | ArtistStructures.Firebase.Logging = None):

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
                datas = o_f.override_dicts_recursive(ArtistStructures.Default.DEFAULT, datas)


            self.name = datas["name"]
            self.proof = datas["proof"]
            self.vadb_info = self.VADBInfo(datas["vadb_info"])
            self.discord_info = self.DiscordInfo(datas["discord_info"])
            self.states = self.States(datas["states"])
            self.details = self.Details(datas["details"])

            self.get_logs()

        class VADBInfo(ArtistDataStructure):
            """Stores VADB-Related info.
            artist_id: int
            page: str
            """
            def __init__(self, datas: dict = None):
                self.artist_id = datas["artist_id"]
                self.page = datas["page"]

        class DiscordInfo(ArtistDataStructure):
            """Stores Discord-related info.
            logs: list[o_f.Log]
            """
            def __init__(self, datas):
                self.logs = self.Logs(datas["logs"])

            class Logs(ArtistDataStructure):
                """Stores logs.
                pending: list[o_f.Log]
                editing: list[o_f.Log]"""
                def __init__(self, datas: dict = None):
                    self.pending = create_log_list(datas["pending"])
                    self.editing = create_log_list(datas["editing"])

        class States(ArtistDataStructure):
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

        class Details(ArtistDataStructure):
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

            class Images(ArtistDataStructure):
                """Stores the images of the artist.
                avatar_url: str
                banner_url: str
                """
                def __init__(self, datas: dict = None):
                    self.avatar_url = datas["avatar_url"]
                    self.banner_url = datas["banner_url"]

            class MusicInfo(ArtistDataStructure):
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
                    await ctx.author.send("Other artist(s) found with this name. Please check if you have a duplicate submission.\nUse `##cancel` if you think you have a different artist, or type anything to continue.\nIf you are submitting an artist with the same exact name as these results, try to add extra characters on the name to avoid duplicates.", embed=generate_search_embed(search_result))
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


        async def post_log(self, log_type: l_l.LogTypes.Pending | l_l.LogTypes.Editing, user_id: int):
            """Posts logs to channels by type."""
            async def post_log_to_channels(channel_dicts):
                log_messages = []
                for channel_dict in channel_dicts:
                    if not isinstance(channel_dict, dict):
                        continue

                    channel: nx.TextChannel = vrs.global_bot.get_channel(int(channel_dict["channel"]))
                    if channel is None:
                        continue
                    main_message: nx.Message = await channel.send(f"{log_type.title_str} The PA moderators will look into this.",
                        embed=await self.generate_embed())

                    proof_message: nx.Message = await channel.send(self.proof)

                    log_message = {
                            "main": o_f.MessagePointer(channel_id=channel.id, message_id=main_message.id).get_dict(),
                            "proof": o_f.MessagePointer(channel_id=channel.id, message_id=proof_message.id).get_dict(),
                        }

                    log_messages.append(log_message)

                return [l_l.Log({
                    "message": log_message,
                    "user_id": user_id
                }) for log_message in log_messages]

            await post_log_to_channels(f_i.get_data(["logData", "dump"]))
            live_logs = await post_log_to_channels(f_i.get_data(["logData", "live"]))
            if log_type == l_l.LogTypes.PENDING:
                self.discord_info.logs.pending = live_logs
            elif log_type == l_l.LogTypes.EDITING:
                self.discord_info.logs.editing = live_logs

            ArtistStructures.Firebase.Logging(self).send_data(log_type)

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
                    await main_message.delete()
                    proof_message = await log.message.proof.get_message()
                    await proof_message.delete()
                
                f_i.delete_data(log_type.path + [str(self.vadb_info.artist_id)])
            
            self.discord_info.logs.pending = await delete_log(self.discord_info.logs.pending, l_l.LogTypes.PENDING)
            self.discord_info.logs.editing = await delete_log(self.discord_info.logs.editing, l_l.LogTypes.EDITING)


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

            class Details(ArtistDataStructure):
                """Contains details."""
                def __init__(self, datas: dict = None):
                    self.avatarUrl = datas["avatarUrl"]
                    self.bannerUrl = datas["bannerUrl"]
                    self.socials = datas["socials"]


    class Firebase:
        """Contains classes for Firebase Interaction."""

        class Logging(ArtistDataStructure):
            """Class for logging and receiving pending and editing artists."""
            def __init__(self, datas: dict | ArtistStructures.Default = None):
                if isinstance(datas, ArtistStructures.Default):
                    datas = {
                        "artist_id": datas.vadb_info.artist_id,
                        "data": datas
                    }
                elif isinstance(datas, dict):
                    datas = o_f.override_dicts_recursive(self.get_default_dict(), datas)
                else:
                    datas = self.get_default_dict()

                self.artist_id = datas["artist_id"]
                self.datas = datas["data"]

            def send_data(self, log_type: l_l.LogTypes.Pending | l_l.LogTypes.Editing):
                """Sends the data to Firebase."""
                f_i.edit_data(log_type.path, {self.artist_id: self.datas.get_dict()})



def search_for_artist(search_term: str) -> list[ArtistStructures.Default]:
    """Searches for artists on VADB."""

    search_term_url = ul.quote_plus(search_term)
    search_term_url = search_term_url.replace("+", "%20")
    try:
        response = v_i.make_request("GET", f"/search/{search_term_url}")
    except req.exceptions.HTTPError:
        return None

    artists_data = response["data"]
    artist_list = [ArtistStructures.Default(ArtistStructures.VADB.Receive(artist_data)) for artist_data in artists_data]

    return artist_list

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
    artist = ArtistStructures.Default(ArtistStructures.VADB.Receive(v_i.make_request("GET", f"/artist/{artist_id}")["data"]))
    return artist

def create_log_list(logs):
    """Creates a list of log objects."""
    return [l_l.Log(log) for log in logs] if logs is not None else None
