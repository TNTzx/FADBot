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
import abc
from typing import Union
import urllib.parse as ul
# from pprint import pprint
import discord
from discord.enums import DefaultAvatar
import discord.ext.commands as cmds

import tldextract as tld

from functions import other_functions as o_f


DEFAULT_IMAGE = "https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg"

class ArtistDataStructure(abc.ABC):
    """ABC that defines a common data structure."""

    def get_default_dict(self):
        return self.__class__(Structures.Default()).to_dict()

    @abc.abstractmethod
    def to_dict(self):
        """Turns the data into a dictionary."""
        return o_f.get_dict_attr(self)

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
                self.status = o_f.Match(status_dict, datas["status"])

                availability_dict = {
                    0: "Verified",
                    1: "Disallowed",
                    2: "Contact Required",
                    3: "Varies"
                }
                self.availability = o_f.Match(availability_dict, datas["availability"])

                self.usage_rights = datas["usage_rights"]

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

            def to_dict(self):
                return {
                    "description": self.description,
                    "notes": self.notes
                }

        def get_default_dict(self):
            pass
        def to_dict(self):
            return super().to_dict()


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

                def get_default_dict(self):
                    return super().get_default_dict()
                def to_dict(self):
                    return super().to_dict()
            
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

                
                def get_default_dict(self):
                    return super().get_default_dict()
                def to_dict(self):
                    return super().to_dict()


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
                def __init__(self, datas: dict = None):
                    self.avatarUrl = datas["avatarUrl"]
                    self.bannerUrl = datas["bannerUrl"]
                    self.socials = datas["socials"]

            
            def get_default_dict(self):
                return super().get_default_dict()
            def to_dict(self):
                return super().to_dict()
