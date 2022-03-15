"""Contains code for image handling."""


import os
import io

import urllib.parse as urlparse
import requests as req

import PIL.Image as PIL

import backend.databases.vadb.vadb_interact as v_i
import backend.utils.new_dataclass as dt

from .. import artist_struct as a_s


class Image(dt.APIDataclass):
    """Defines an image for uploading to VADB."""
    def __init__(self, name: str, data: PIL.Image | bytes):
        self.name = name

        self.pil_image = data

        if isinstance(data, PIL.Image):
            with io.BytesIO() as data_bytes:
                data.save(data_bytes, format = "PNG")
                self.data = data_bytes.getvalue()
        else:
            self.data = data

    def to_payload(self) -> dict:
        return (self.name, self.data, "image/png")


    @classmethod
    def from_url(cls, url: str):
        """Gets an Image from a URL."""
        url_parse = urlparse.urlparse(url)
        name = os.path.basename(url_parse.path)
        response = req.get(url, stream = True)
        data = PIL.open(response.raw)
        return cls(
            name = name,
            data = data
        )

    @classmethod
    def from_artist(cls, artist_id: int, type_: str):
        """Gets the avatar / banner of an artist."""
        return cls.from_url(f"{v_i.API_IMAGE_LINK}/{type_}/{artist_id}")

class ImageTypes:
    """Contains image types."""
    avatar = "avatar"
    banner = "banner"


DEFAULT_IMAGE = Image.from_url("https://p1.pxfuel.com/preview/722/907/815/question-mark-hand-drawn-solution-think.jpg")

class ImageInfo(a_s.ArtistStruct):
    """Stores the images of the artist."""
    def __init__(
            self,
            avatar: Image = DEFAULT_IMAGE,
            banner: Image = DEFAULT_IMAGE
            ):
        self.avatar = avatar
        self.banner = banner
