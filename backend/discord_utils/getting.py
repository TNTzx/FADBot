"""Contains logic for getting channels from ids, user from id, etc."""


import re

import nextcord as nx
import nextcord.ext.commands as nx_cmds

import global_vars
import backend.exc_utils as exc_utils

from . import disc_exc


def get_id_from_mention(mention_str: str):
    """Gets the ID from a mention."""
    if not (mention_str.startswith("<") and mention_str.endswith(">")):
        raise disc_exc.NotMention(mention_str)

    try:
        return int(mention_str[2:-1])
    except (ValueError, TypeError) as exc:
        raise disc_exc.NotMention(mention_str) from exc

async def get_id_from_mention_warn(ctx, mention_str: str):
    """Like `get_id_from_mention`, but with warning the user."""
    try:
        return get_id_from_mention(mention_str)
    except disc_exc.NotMention:
        await exc_utils.SendFailed(
            error_place = exc_utils.ErrorPlace.from_context(ctx),
            suffix = f"{mention_str} is not a mention! Make sure that this text turns blue when you send the message!"
        ).send()


def emoji_id_from_str(emoji_str: str):
    """Returns the emoji's ID from the emoji string."""
    regex = "^<a?:.*:(.+)>$"
    group = 1
    search = re.search(regex, emoji_str)
    if search is None:
        raise disc_exc.NotEmojiStr(emoji_str)

    return int(search.group(group))

async def emoji_id_from_str_warn(ctx: nx_cmds.Context, emoji_str: str):
    """Like `emoji_id_from_str`, but with warning the user."""
    try:
        return emoji_id_from_str(emoji_str)
    except disc_exc.NotEmojiStr:
        await exc_utils.SendFailed(
            error_place = exc_utils.ErrorPlace.from_context(ctx),
            suffix = f"{emoji_str} is not an emoji!"
        ).send()


def emoji_from_id(emoji_id: int):
    """Returns the `Emoji` from the emoji ID."""
    emoji = global_vars.bot.get_emoji(emoji_id)
    if emoji is None:
        raise disc_exc.EmojiNotFound(emoji_id)

    return emoji

async def emoji_from_id_warn(ctx: nx_cmds.Context, emoji_id: int):
    """Like `emoji_from_id`, but with warning the user."""
    try:
        return emoji_from_id(emoji_id)
    except disc_exc.EmojiNotFound:
        await exc_utils.SendFailed(
            error_place = exc_utils.ErrorPlace.from_context(ctx),
            suffix = f"Emoji ID {emoji_id} not found! Maybe this emoji is in a server where this bot isn't in?"
        ).send()


def channel_from_id(channel_id: int):
    """Takes in a channel mention then returns the channel."""
    channel = global_vars.bot.get_channel(channel_id)
    if channel is None or not isinstance(channel, nx.TextChannel):
        raise disc_exc.ChannelNotFound(channel_id)

    return channel

async def channel_from_id_warn(ctx: nx_cmds.Context, channel_id: int):
    """Like `channel_from_id`, but with warning the user."""
    try:
        return channel_from_id(channel_id)
    except disc_exc.ChannelNotFound:
        await exc_utils.SendFailed(
            error_place = exc_utils.ErrorPlace.from_context(ctx),
            suffix = f"Channel ID {channel_id} not found!"
        ).send()


def user_from_id(user_id: int):
    """Takes in a user ID and returns the user."""
    user = global_vars.bot.get_user(user_id)
    if user is None:
        raise disc_exc.UserNotFound(user_id)

    return user

async def user_from_id_warn(ctx: nx_cmds.Context, user_id: int):
    """Like `user_from_id`, but with warning the user."""
    try:
        return user_from_id(user_id)
    except disc_exc.UserNotFound:
        await exc_utils.SendFailed(
            error_place = exc_utils.ErrorPlace.from_context(ctx),
            suffix = f"User ID {user_id} not found!"
        ).send()
