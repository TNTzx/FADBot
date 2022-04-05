"""Contains all cogs used for the bot."""


from .artist_utils import *
from .essentials import *
from .moderation import *

try:
    from .testcode import CogTest
except ImportError:
    pass
