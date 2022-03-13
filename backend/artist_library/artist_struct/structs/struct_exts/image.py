"""Contains code for image handling."""


import os
import typing as typ

import urllib.parse as urllib
import requests as req

from PIL import Image as PIL

import backend.utils.new_dataclass as dt


class Image(dt.APIDataclass):
    """Defines an image for uploading to VADB."""
    def __init__(self, name: str, data: PIL.Image):
        self.name = name
        self.data = data

    def get_mime_type(self):
        """Gets the mime type."""
        return PIL.MIME[self.data.format]


    def to_payload(self) -> dict:
        return (self.name, self.data, self.get_mime_type())


class ImageUrl(dt.Dataclass):
    """Defines an image URL. Always convert to an image."""
    def __init__(self, url: str):
        self.url = url

    def to_image(self):
        """Turn into an image."""
        url_parse = urllib.urlparse(self.url)
        name = os.path.basename(url_parse.path)
        data = PIL.open(req.get(self.url, stream = True).raw)
        return Image(name = name, data = data)
