"""Module that contains the classes for artist control."""

# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods


import urllib.parse as ul
# from pprint import pprint
import discord
import discord.ext.commands as cmds

import tldextract as tld

import main
from functions.artist_related import asking as ask
from functions.exceptions import custom_exc as c_exc


DEFAULT_IMAGE = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"

def make_embed():
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

class Artist:
    """Class for artist."""
    def __init__(self, generate: dict = None):
        if generate is None:
            self.vadb_page = "https://fadb.live/"
            self.artist_data = self.ArtistData()
        else:
            self.__dict__.update(generate)

    class ArtistData:
        """Class for data of artist."""
        def __init__(self):
            self.artist_id = None
            self.name = "default name"
            self.proof = DEFAULT_IMAGE
            self.status = 2
            self.availability = 0

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


        async def set_proof(self, ctx, skippable=False):
            """Sets the proof."""
            self.proof = await ask.wait_for_response(ctx,
                "Please send proof that you contacted the artist.",
                "Take a screenshot of the email/message that the artist sent you that proves the artist's verification/unverification. You can only upload 1 image/link.",
                ask.OutputTypes.image,
                skippable=skippable, skip_default=self.proof
            )

        async def set_availability(self, ctx, skippable=False):
            """Sets the availability."""
            availability = await ask.wait_for_response(ctx,
                "Is the artist verified, disallowed, or does it vary between songs?",
                "\"Verified\" means that the artist's songs are allowed to be used for custom PA levels.\n\"Disallowed\" means that the artist's songs cannot be used.\n\"Varies\" means that it depends per song, for example, remixes aren't allowed for use but all their other songs are allowed.",
                ask.OutputTypes.text, choices=["Verified", "Disallowed", "Varies"],
                skippable=skippable, skip_default=None
            )
            availability_dict = {
                "verified": 0,
                "disallowed": 1,
                "varies": 3,
                None: self.availability
            }
            self.availability = availability_dict[availability]

        async def set_name(self, ctx, skippable=False):
            """Sets the name of the artist."""
            self.name = await ask.wait_for_response(ctx,
                "Artist Name",
                "Send the artist name.",
                ask.OutputTypes.text,
                skippable=skippable, skip_default=self.name
            )

        async def set_aliases(self, ctx, skippable=True):
            """Sets the aliases of the artist."""
            alias_names = await ask.wait_for_response(ctx,
                "Artist Aliases",
                "Send other names that the artist goes by.",
                ask.OutputTypes.listing,
                skippable=skippable, skip_default=None
            )
            self.aliases = [{"name": alias} for alias in alias_names] if not alias_names is None else self.aliases

        async def set_desc(self, ctx, skippable=True):
            """Sets the description."""
            self.description = await ask.wait_for_response(ctx,
                "Send a description about the artist.",
                "You can put information about the artist here. Their bio, how their music is created, etc. could work.",
                ask.OutputTypes.text,
                skippable=skippable, skip_default=self.description
            )

        async def set_notes(self, ctx, skippable=True):
            """Sets the notes."""
            self.notes = await ask.wait_for_response(ctx,
                "Notes",
                "Send other notes you want to put in.",
                ask.OutputTypes.text,
                skippable=skippable, skip_default=self.notes
            )

        async def set_avatar(self, ctx, skippable=True):
            """Sets the avatar of the artist."""
            self.details.avatar = await ask.wait_for_response(ctx,
                "Send an image to an avatar of the artist.",
                "This is the profile picture that the artist uses.",
                ask.OutputTypes.image,
                skippable=skippable, skip_default=self.details.avatar
            )

        async def set_banner(self, ctx, skippable=True):
            """Sets the banner of the artist."""
            self.details.banner = await ask.wait_for_response(ctx,
                "Send an image to the banner of the artist.",
                "This is the banner that the artist uses.",
                ask.OutputTypes.image,
                skippable=skippable, skip_default=self.details.banner
            )

        async def set_tracks(self, ctx, skippable=True):
            """Sets the number of tracks."""
            self.tracks = await ask.wait_for_response(ctx,
                "How many tracks does the artist have?",
                "This is the count for how much music the artist has produced. It can easily be found on Soundcloud pages, if you were wondering.",
                ask.OutputTypes.number,
                skippable=skippable, skip_default=self.tracks
            )

        async def set_genre(self, ctx, skippable=True):
            """Sets the genre."""
            self.genre = await ask.wait_for_response(ctx,
                "What is the genre of the artist?",
                "This is the type of music that the artist makes.",
                ask.OutputTypes.text,
                skippable=skippable, skip_default=self.genre
            )

        async def set_usage_rights(self, ctx, skippable=True):
            """Sets the usage rights of the artist."""
            usage_rights = await ask.wait_for_response(ctx,
                "What are the usage rights for the artist?",
                "This is where you put in the usage rights. For example, if remixes aren't allowed, you can type in `\"Remixes: Disallowed\"`. Add more items as needed.",
                ask.OutputTypes.dictionary, choices_dict=["Verified", "Disallowed"],
                skippable=skippable, skip_default={}
            )
            usage_list = []
            for right, state in usage_rights.items():
                value = state == "verified"
                usage_list.append({
                    "name": right,
                    "value": value
                })
            self.usage_rights = usage_list if len(usage_list) > 1 else self.usage_rights

        async def set_socials(self, ctx, skippable=True):
            """Sets the socials of the artist."""
            socials = await ask.wait_for_response(ctx,
                "Please put some links for the artist's social media here.",
                "This is where you put in links for the artist's socials such as Youtube, Spotify, Bandcamp, etc.",
                ask.OutputTypes.links,
                skippable=skippable, skip_default=[]
            )
            social_list = []
            for link in socials:
                type_link: str = tld.extract(link).domain
                type_link = type_link.capitalize()
                social_list.append({
                    "link": link,
                    "type": type_link
                })
            self.details.socials = social_list if len(social_list) > 0 else self.details.socials


        async def edit_loop(self, ctx: cmds.Context):
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

                message: discord.Message = await ask.waiting(ctx)
                command = message.content.split(" ")

                if command[0].startswith(f"{main.CMD_PREFIX}edit"):
                    command_to_get = command_dict.get(command[1] if len(command) > 1 else None, None)

                    if command_to_get is None:
                        await ask.send_error(ctx, f"You didn't specify a valid property! The valid properties are `{'`, `'.join(command_dict.keys())}`")
                        continue

                    await command_to_get(ctx, skippable=True)

                elif command[0] == f"{main.CMD_PREFIX}submit":
                    break

                elif command[0] == f"{main.CMD_PREFIX}cancel":
                    raise c_exc.ExitFunction("Exited Function.")

                else:
                    await ask.send_error(ctx, "You didn't send a command!")

