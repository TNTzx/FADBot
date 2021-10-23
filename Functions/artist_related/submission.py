"""Module that contains the classes for artist control."""

# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods


import asyncio
import urllib.parse as ul
# from pprint import pprint
import discord
import discord.ext.commands as cmds
import requests as req
import tldextract as tld

import main
from Functions import CustomExceptions as ce
from Functions import ExtraFunctions as ef
from Functions.ArtistManagement import ArtistDataFormat as adf
from Functions import FirebaseInteraction as fi
from Functions import RequestAPI as rqapi


TIMEOUT = 60 * 10
DEFAULT_IMAGE = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"

class ArtistFunctions:
    """Functions for artist management."""

    async def check_if_using_command(self, author_id):
        """Returns true if the user is using the command."""
        users_using = fi.get_data(["artistData", "pending", "isUsingCommand"])
        return author_id in list(users_using)

    async def add_is_using_command(self, author_id):
        """Adds the user as one that is using the command."""
        fi.append_data(["artistData", "pending", "isUsingCommand"], [author_id])

    async def delete_is_using_command(self, author_id):
        """Deletes the user as one that is using the command."""
        data = fi.get_data(["artistData", "pending", "isUsingCommand"])
        try:
            data.remove(author_id)
        except ValueError:
            pass
        fi.edit_data(["artistData", "pending"], {"isUsingCommand": data})


    async def send_error(self, ctx, suffix):
        """Sends an error, but with a syntax."""
        await ef.send_error(ctx, f"{suffix} Try again.", send_author=True)

    async def waiting(self, ctx: cmds.Context):
        """Wait for a message then return the response."""
        try:
            check = lambda msg: ctx.author.id == msg.author.id and isinstance(msg.channel, discord.channel.DMChannel)
            response: discord.Message = await main.bot.wait_for("message", check=check, timeout=TIMEOUT)
        except asyncio.TimeoutError as exc:
            await self.delete_is_using_command(ctx.author.id)
            await ef.send_error(ctx, "Command timed out. Please use the command again.")
            raise ce.ExitFunction("Exited Function.") from exc
        return response

    async def wait_for_response(self, ctx,
            title, description, output_type,
            choices: list[str] = None, choices_dict: list[str] = None,
            skippable=False, skip_default=""):
        """Returns the response, but with checks."""

        async def check_has_required():
            if choices is not None:
                return len(choices) > 0
            return False
        async def check_has_dict():
            if choices is not None:
                return len(choices_dict) > 0
            return False

        async def reformat(response: discord.Message):
            async def number():
                if not response.content.isnumeric():
                    await self.send_error(ctx, "That's not a number!")
                    return None
                return int(response.content)

            async def text():
                if await check_has_required():
                    if not response.content.lower() in [x.lower() for x in choices]:
                        await self.send_error(ctx, "You didn't send a choice in the list of choices!")
                        return None
                    return response.content.lower()
                if response.content == "":
                    await self.send_error(ctx, "You didn't send anything!")
                    return None
                return response.content

            async def links():
                async def check_link(url):
                    try:
                        req.head(url)
                    except req.exceptions.RequestException as exc:
                        await self.send_error(ctx, f"You didn't send valid links! Here's the error:\n```{str(exc)}```")
                        return None
                    return url

                links = response.content.split("\n")
                for link in links:
                    link = await check_link(link)
                    if link is None:
                        return None
                return links

            async def image():
                async def check_image(image_url):
                    supported_formats = ["png", "jpg", "jpeg"]

                    try:
                        image_request = req.head(image_url)
                    except req.exceptions.RequestException as exc:
                        await self.send_error(ctx, f"You didn't send a valid image/link! Here's the error:\n```{str(exc)}```")
                        return None

                    if not image_request.headers["Content-Type"] in [f"image/{x}" for x in supported_formats]:
                        await self.send_error(ctx, f"You sent a link to an unsupported file format! The formats allowed are `{'`, `'.join(supported_formats)}`.")
                        return None

                    return image_url

                async def attachments():
                    return await check_image(response.attachments[0].url)

                async def link():
                    return await check_image(response.content)


                if not len(response.attachments) == 0:
                    return await attachments()
                else:
                    return await link()


            async def listing():
                return response.content.split("\n")

            async def dictionary():
                entries = response.content.split("\n")
                entry_dict = {}
                for entry in entries:
                    item = entry.split(":")
                    item = [x.lstrip(' ') for x in item]
                    try:
                        if not len(item) == 2:
                            raise IndexError

                        if not await check_has_dict():
                            entry_dict[item[0]] = item[1]
                        else:
                            entry_dict[item[0]] = item[1].lower()
                    except (KeyError, IndexError):
                        await self.send_error(ctx, "Your formatting is wrong!")
                        return None

                    if not item[1].lower() in [x.lower() for x in choices_dict]:
                        await self.send_error(ctx, f"Check if the right side of the colons contain these values: `{'`, `'.join([x for x in choices_dict])}`")
                        return None
                return entry_dict

            if output_type == OutputTypes.number:
                return await number()
            elif output_type == OutputTypes.text:
                return await text()
            elif output_type == OutputTypes.links:
                return await links()
            elif output_type == OutputTypes.image:
                return await image()
            elif output_type == OutputTypes.listing:
                return await listing()
            elif output_type == OutputTypes.dictionary:
                return await dictionary()

        success = True
        while success:
            title_form = title if not skippable else f"{title} (skippable)"
            embed = discord.Embed(title=title_form, description=description)
            embed.add_field(name="_ _", value="_ _", inline=False)

            field_name = f"You have to send {output_type['prefix']} {output_type['type']}!"

            if not await check_has_required():
                field_desc = f"__Here is an example of what you have to send:__\n`{output_type['example']}`"
                embed.add_field(name=field_name, value=field_desc, inline=False)
            else:
                field_desc = f"Choose from one of the following choices: \n`{'`, `'.join(choices)}`"
                embed.add_field(name=field_name, value=field_desc, inline=False)

            embed.add_field(name="_ _", value="_ _", inline=False)

            skip_str = f"This command times out in {ef.format_time(TIMEOUT)}. \nUse {main.CMD_PREFIX}cancel to cancel the current command." + (f"\nUse {main.CMD_PREFIX}skip to skip this section." if skippable else "")
            embed.set_footer(text=skip_str)

            await ctx.author.send(embed=embed)

            response = await self.waiting(ctx)

            if response.content == f"{main.CMD_PREFIX}cancel":
                raise ce.ExitFunction("Exited Function.")
            elif response.content == f"{main.CMD_PREFIX}skip":
                if skippable:
                    await ctx.author.send("Section skipped.")
                    return skip_default
                else:
                    await self.send_error(ctx, "You can't skip this section!")
                    continue

            try:
                response = await reformat(response)
            except Exception as exc:
                await self.delete_is_using_command(ctx.author.id)
                raise exc
            success = (response is None)
        return response

class OutputTypes():
    """Available output types for the wait_for_response() function."""
    number = {"type": "number",
        "prefix": "a",
        "example": "1234531"}
    text = {"type": "text",
        "prefix": "some",
        "example": "This is a very cool string of text!"}
    links = {"type": "links",
        "prefix": "a list of",
        "example": "https://www.youtube.com/FunnyArtistName\nhttps://open.spotify.com/AnotherFunnyArtistName"}
    image = {"type": "image",
        "prefix": "an",
        "example": "https://cdn.discordapp.com/attachments/888419023237316609/894910496199827536/beanss.jpg`\n`(OR you can upload your images as attachments like normal!)"}
    listing = {"type": "list",
        "prefix": "a", "example":
        "This is the first item on the list!\nThis is the second item on the list!\nThis is the third item on the list!"}
    dictionary = {"type": "dictionary",
        "prefix": "a",
        "example": "Remixes: Disallowed\nA very specific song: Verified"}

class Artist:
    """Class for artist."""
    def __init__(self):
        self.proof = DEFAULT_IMAGE
        self.vadb_page = "https://fadb.live/"
        self.artist_data = self.ArtistData()

    class ArtistData:
        """Class for data of artist."""
        def __init__(self):
            self.status = 2
            self.availability = 0
            self.artist_id = None
            self.name = "default name"
            self.aliases = []
            self.description = "I am a contacted artist! :D"
            self.tracks = 0
            self.genre = "Mixed"
            self.usage_rights = []
            self.details = self.Details()
            self.notes = "None"

        class Details:
            """Class for the avatar, banner, and socials of the artist."""
            def __init__(self):
                self.avatar = DEFAULT_IMAGE
                self.banner = DEFAULT_IMAGE
                self.socials = []


        def dict_init(self):
            """Returns the dictionary required to make an artist at VADB's database."""
            return {
                "name": self.name,
                "status": self.status,
                "availability": self.availability
            }

        def dict_edit(self):
            """Returns the dictionary required to edit an artist at VADB's database."""
            return {
                "name": self.name,
                "aliases": self.aliases,
                "description": self.description,
                "tracks": self.tracks,
                "genre": self.genre,
                "status": self.status,
                "availability": self.availability,
                "notes": self.notes,
                "usageRights": self.usage_rights,
                "avatarUrl": self.details.avatar,
                "bannerUrl": self.details.banner,
                "socials": self.details.socials
            }

class User:
    """Stores info about the user."""
    def __init__(self):
        self.user_id = None


class Submission(ArtistFunctions):
    """Main submission class."""
    def __init__(self):
        self.user = User()
        self.artist = Artist()


    async def set_proof(self, ctx, skippable=False):
        """Sets the proof."""
        self.artist.proof = await self.wait_for_response(ctx,
            "Please send proof that you contacted the artist.",
            "Take a screenshot of the email/message that the artist sent you that proves the artist's verification/unverification. You can only upload 1 image/link.",
            OutputTypes.image,
            skippable=skippable, skip_default=self.artist.proof
        )

    async def set_availability(self, ctx, skippable=False):
        """Sets the availability."""
        availability = await self.wait_for_response(ctx,
            "Is the artist verified, disallowed, or does it vary between songs?",
            "\"Verified\" means that the artist's songs are allowed to be used for custom PA levels.\n\"Disallowed\" means that the artist's songs cannot be used.\n\"Varies\" means that it depends per song, for example, remixes aren't allowed for use but all their other songs are allowed.",
            OutputTypes.text, choices=["Verified", "Disallowed", "Varies"],
            skippable=skippable, skip_default=None
        )
        availability_dict = {
            "verified": 0,
            "disallowed": 1,
            "varies": 3,
            None: self.artist.artist_data.availability
        }
        self.artist.artist_data.availability = availability_dict[availability]

    async def set_name(self, ctx, skippable=False):
        """Sets the name of the artist."""
        self.artist.artist_data.name = await self.wait_for_response(ctx,
            "Artist Name",
            "Send the artist name.",
            OutputTypes.text,
            skippable=skippable, skip_default=self.artist.artist_data.name
        )

    async def set_aliases(self, ctx, skippable=True):
        """Sets the aliases of the artist."""
        alias_names = await self.wait_for_response(ctx,
            "Artist Aliases",
            "Send other names that the artist goes by.",
            OutputTypes.listing,
            skippable=skippable, skip_default=None
        )
        self.artist.artist_data.aliases = [{"name": alias} for alias in alias_names] if not alias_names is None else self.artist.artist_data.aliases

    async def set_desc(self, ctx, skippable=True):
        """Sets the description."""
        self.artist.artist_data.description = await self.wait_for_response(ctx,
            "Send a description about the artist.",
            "You can put information about the artist here. Their bio, how their music is created, etc. could work.",
            OutputTypes.text,
            skippable=skippable, skip_default=self.artist.artist_data.description
        )

    async def set_notes(self, ctx, skippable=True):
        """Sets the notes."""
        self.artist.artist_data.notes = await self.wait_for_response(ctx,
            "Notes",
            "Send other notes you want to put in.",
            OutputTypes.text,
            skippable=skippable, skip_default=self.artist.artist_data.notes
        )

    async def set_avatar(self, ctx, skippable=True):
        """Sets the avatar of the artist."""
        self.artist.artist_data.details.avatar = await self.wait_for_response(ctx,
            "Send an image to an avatar of the artist.",
            "This is the profile picture that the artist uses.",
            OutputTypes.image,
            skippable=skippable, skip_default=self.artist.artist_data.details.avatar
        )

    async def set_banner(self, ctx, skippable=True):
        """Sets the banner of the artist."""
        self.artist.artist_data.details.banner = await self.wait_for_response(ctx,
            "Send an image to the banner of the artist.",
            "This is the banner that the artist uses.",
            OutputTypes.image,
            skippable=skippable, skip_default=self.artist.artist_data.details.banner
        )

    async def set_tracks(self, ctx, skippable=True):
        """Sets the number of tracks."""
        self.artist.artist_data.tracks = await self.wait_for_response(ctx,
            "How many tracks does the artist have?",
            "This is the count for how much music the artist has produced. It can easily be found on Soundcloud pages, if you were wondering.",
            OutputTypes.number,
            skippable=skippable, skip_default=self.artist.artist_data.tracks
        )

    async def set_genre(self, ctx, skippable=True):
        """Sets the genre."""
        self.artist.artist_data.genre = await self.wait_for_response(ctx,
            "What is the genre of the artist?",
            "This is the type of music that the artist makes.",
            OutputTypes.text,
            skippable=skippable, skip_default=self.artist.artist_data.genre
        )

    async def set_usage_rights(self, ctx, skippable=True):
        """Sets the usage rights of the artist."""
        usage_rights = await self.wait_for_response(ctx,
            "What are the usage rights for the artist?",
            "This is where you put in the usage rights. For example, if remixes aren't allowed, you can type in `\"Remixes: Disallowed\"`. Add more items as needed.",
            OutputTypes.dictionary, choices_dict=["Verified", "Disallowed"],
            skippable=skippable, skip_default={}
        )
        usage_list = []
        usage_list.append({
                "name": "Some songs" if self.artist.artist_data.availability == 2 else "All songs",
                "value": True if self.artist.artist_data.availability == 0 else False
            })
        for right, state in usage_rights.items():
            value = state == "verified"
            usage_list.append({
                "name": right,
                "value": value
            })
        self.artist.artist_data.usage_rights = usage_list if len(usage_list) > 1 else self.artist.artist_data.usage_rights

    async def set_socials(self, ctx, skippable=True):
        """Sets the socials of the artist."""
        socials = await self.wait_for_response(ctx,
            "Please put some links for the artist's social media here.",
            "This is where you put in links for the artist's socials such as Youtube, Spotify, Bandcamp, etc.",
            OutputTypes.links,
            skippable=skippable, skip_default=[]
        )
        social_list = []
        for link in socials:
            type_link = tld.extract(link).domain
            type_link = type_link.capitalize()
            social_list.append({
                "link": link,
                "type": type_link
            })
        self.artist.artist_data.details.socials = social_list if len(social_list) > 0 else self.artist.artist_data.details.socials


    async def generate_dict(self):
        """Generates a dictionary of the attributes."""
        data = adf.data_format
        data["userInfo"]["id"] = self.user.user_id
        data["artistInfo"]["proof"] = self.artist.proof
        data["artistInfo"]["vadbPage"] = self.artist.vadb_page
        data["artistInfo"]["data"]["status"] = self.artist.artist_data.status
        data["artistInfo"]["data"]["availability"] = self.artist.artist_data.availability
        data["artistInfo"]["data"]["name"] = self.artist.artist_data.name
        data["artistInfo"]["data"]["aliases"] = self.artist.artist_data.aliases
        data["artistInfo"]["data"]["description"] = self.artist.artist_data.description
        data["artistInfo"]["data"]["tracks"] = self.artist.artist_data.tracks
        data["artistInfo"]["data"]["genre"] = self.artist.artist_data.genre
        data["artistInfo"]["data"]["usageRights"] = self.artist.artist_data.usage_rights
        data["artistInfo"]["data"]["notes"] = self.artist.artist_data.notes
        data["artistInfo"]["data"]["details"]["avatarUrl"] = self.artist.artist_data.details.avatar
        data["artistInfo"]["data"]["details"]["bannerUrl"] = self.artist.artist_data.details.banner
        data["artistInfo"]["data"]["details"]["socials"] = self.artist.artist_data.details.socials
        return data

    async def generate_from_dict(self, data):
        """Generates a Submission object from a dictionary."""
        self.user.user_id = data["userInfo"]["id"]
        self.artist.proof = data["artistInfo"]["proof"]
        self.artist.vadb_page = data["artistInfo"]["vadbPage"]
        self.artist.artist_data.status = data["artistInfo"]["data"]["status"]
        self.artist.artist_data.availability = data["artistInfo"]["data"]["availability"]
        self.artist.artist_data.name = data["artistInfo"]["data"]["name"]
        self.artist.artist_data.aliases = data["artistInfo"]["data"]["aliases"]
        self.artist.artist_data.description = data["artistInfo"]["data"]["description"]
        self.artist.artist_data.tracks = data["artistInfo"]["data"]["tracks"]
        self.artist.artist_data.genre = data["artistInfo"]["data"]["genre"]
        self.artist.artist_data.usage_rights = data["artistInfo"]["data"]["usageRights"]
        self.artist.artist_data.details.avatar = data["artistInfo"]["data"]["details"]["avatarUrl"]
        self.artist.artist_data.details.banner = data["artistInfo"]["data"]["details"]["bannerUrl"]
        self.artist.artist_data.details.socials = data["artistInfo"]["data"]["details"]["socials"]


    status_keys = {
        0: "Completed",
        1: "No Contact",
        2: "Pending",
        3: "Requested"
    }

    availability_keys = {
        0: "Verified",
        1: "Disallowed",
        2: "Contact Required",
        3: "Varies"
    }

    color_keys = {
        "Green": 0x00FF00,
        "Red": 0xFF0000,
        "Yellow": 0xFFFF00,
        "Blue": 0x0000FF
    }

    async def generate_embed(self, editing=False):
        """Generates an embed."""
        description = self.artist.artist_data.description

        artist_name = self.artist.artist_data.name
        artist_vadb_page = self.artist.vadb_page
        artist_avatar = self.artist.artist_data.details.avatar
        artist_banner = self.artist.artist_data.details.banner

        artist_aliases = self.artist.artist_data.aliases
        alias_list = [alias["name"] for alias in artist_aliases]
        artist_aliases = f"`{'`, `'.join(alias_list)}`" if len(alias_list) > 0 else None

        artist_id = self.artist.artist_data.artist_id
        artist_id = artist_id if not artist_id is None else "Unknown"

        if not self.user.user_id is None:
            user: discord.User = await main.bot.fetch_user(self.user.user_id)
            username = f"{user.name}#{user.discriminator}"
            user_id = user.id
        else:
            username = "Unknown"
            user_id = "Unknown"

        status = self.status_keys[self.artist.artist_data.status]
        availability = self.availability_keys[self.artist.artist_data.availability]

        if status == "Completed":
            if availability == "Verified":
                color = self.color_keys["Green"]
            elif availability == "Disallowed":
                color = self.color_keys["Red"]
            elif availability == "Contact Required":
                color = self.color_keys["Yellow"]
            elif availability == "Varies":
                color = self.color_keys["Blue"]
        elif status in ["No Contact", "Pending"]:
            color = self.color_keys["Yellow"]

        usage_rights = self.artist.artist_data.usage_rights
        if len(usage_rights) > 0:
            usage_list = []
            for entry in usage_rights:
                status_rights = entry["value"]
                usage_list.append(f"{entry['name']}: {'Verified' if status_rights else 'Disallowed'}")
            usage_rights = "\n".join(usage_list)
        else:
            usage_rights = f"All songs: {availability}"

        socials = self.artist.artist_data.details.socials
        if len(socials) > 0:
            socials_list = []
            for entry in socials:
                link, domain = entry["link"], entry["type"]
                socials_list.append(f"[{domain}]({link})")
            socials = " ".join(socials_list)
        else:
            socials = "No socials links!"

        notes = self.artist.artist_data.notes


        def edit_format(prefix):
            return f" (`{main.CMD_PREFIX}edit {prefix}`)" if editing else ""


        embed = discord.Embed(title=f"Artist data for {artist_name}:", description="_ _", color=color)
        embed.set_author(name=f"{artist_name} (ID: {artist_id})", url=artist_vadb_page, icon_url=artist_avatar)
        embed.set_thumbnail(url=artist_avatar)
        embed.set_image(url=artist_banner)
        embed.set_footer(text=f"Verification submitted by {username} ({user_id}).")

        embed.add_field(name=f"Name{edit_format('name')}:", value=f"**{artist_name}**")
        if (not artist_aliases is None) or editing:
            embed.add_field(name=f"Aliases{edit_format('aliases')}:", value=artist_aliases)

        embed.add_field(name=f"Description{edit_format('description')}:", value=description, inline=False)
        embed.add_field(name="VADB Page:", value=f"[Click here!]({artist_vadb_page})", inline=False)

        embed.add_field(name="Status:", value=status)
        embed.add_field(name=f"Availability{edit_format('availability')}:", value=f"**__{availability}__**", inline=False)
        embed.add_field(name=f"Specific usage rights{edit_format('usageRights')}:", value=f"`{usage_rights}`")

        embed.add_field(name=f"Social links{edit_format('socials')}:", value=socials, inline=False)

        embed.add_field(name=f"Other notes{edit_format('notes')}:", value=notes)

        return embed


    async def edit_loop(self, ctx):
        """Initiates an edit loop to edit the attributes."""
        command_dict = {
                "proof": self.set_proof,
                "availability": self.set_availability,
                "name": self.set_name,
                "aliases": self.set_aliases,
                "description": self.set_desc,
                "avatar": self.set_avatar,
                "banner": self.set_banner,
                "tracks": self.set_tracks,
                "genre": self.set_genre,
                "usagerights": self.set_usage_rights,
                "socials": self.set_socials,
                "notes": self.set_notes
            }

        while True:
            await ctx.author.send(f"This is the generated artist profile.\nUse `{main.CMD_PREFIX}edit <property>` to edit a property, `{main.CMD_PREFIX}submit` to submit this verification for approval, or `{main.CMD_PREFIX}cancel` to cancel this command.")

            await ctx.author.send(embed=await self.generate_embed(editing=True))

            message: discord.Message = await self.waiting(ctx)
            command = message.content.split(" ")

            if command[0].startswith(f"{main.CMD_PREFIX}edit"):
                command_to_get = command_dict.get(command[1] if len(command) > 1 else None, None)

                if command_to_get is None:
                    await self.send_error(ctx, f"You didn't specify a valid property! The valid properties are `{'`, `'.join(command_dict.keys())}`")
                    continue

                await command_to_get(ctx, skippable=True)

            elif command[0] == f"{main.CMD_PREFIX}submit":
                break

            elif command[0] == f"{main.CMD_PREFIX}cancel":
                raise ce.ExitFunction("Exited Function.")

            else:
                await self.send_error(ctx, "You didn't send a command!")


    async def format_url_name(self, name: str):
        """Formats the string to be used in VADB requests."""
        name_new = ul.quote(name)
        name_new = name_new.replace("/", "%2f")
        name_new = name_new.replace("%20", "_")
        return name_new

    async def submit_init(self):
        """Submits a request to VADB to make an artist."""
        return rqapi.make_request("POST", "/artist", data=self.artist.artist_data.dict_init())

    async def submit_edit(self, artist_id):
        """Submits a request to VADB to edit an artist."""
        return rqapi.make_request("PATCH", f"/artist/{artist_id}", data=self.artist.artist_data.dict_edit())

    async def send_logs(self):
        """Sends the logs to servers."""
        can_log = fi.get_data(['mainData', 'canLog'])
        channels: list[discord.TextChannel] = [main.bot.get_channel(int(channelId["channel"])) for channelId in can_log]
        channels = [x for x in channels if x is not None]
        for channel in channels:
            await channel.send("A new artist has been submitted and is now waiting approval from PA moderators.")
            await channel.send(embed=await self.generate_embed())


    async def create_vadb_artist(self):
        """Creates a new artist to VADB."""
        await self.send_logs()
        post_data = await self.submit_init()
        await self.submit_edit(post_data["data"]["id"])
