"""Contains logic for command categories."""


import nextcord as nx

import global_vars

from . import cmd_cls


class CmdCategory():
    """Parent class for command categories."""
    name: str = None

    commands: list[cmd_cls.DiscordCommand] = []


    def __init_subclass__(cls) -> None:
        cls.commands: list[cmd_cls.DiscordCommand] = []


    @classmethod
    def get_all_categories(cls):
        """Gets all command categories."""
        return cls.__subclasses__()


    @classmethod
    def register_command(cls, cmd: cmd_cls.DiscordCommand):
        """Registers a command under this category."""
        cls.commands.append(cmd)


    @classmethod
    def generate_embed_all_categories(cls):
        """Generates an embed of all the categories."""
        embed = nx.Embed(
            title = "Help!",
            description = (
                f"**Command Prefix: `{global_vars.CMD_PREFIX}`**\n"
                "This bot was made possible by Nao's website. Go check it out! [**VADB link**](https://fadb.live/)\n"
                "This bot is created by //TNTz.\n\n"
                "Use `##help <command>` to view help for that command!"
            ),
            color = 0xFFAEAE
        )

        emb_all_categs = []
        for category in cls.get_all_categories():
            emb_categ_title = category.name.title()
            emb_categ_desc = [command.get_shorthand() for command in category.commands]
            emb_categ_desc = ", ".join(emb_categ_desc)
            emb_all_categs.append(
                (
                    f"**{emb_categ_title}:**\n"
                    f"`{emb_categ_desc}`"
                )
            )

        embed.add_field(name = "__Commands List__", value = "\n".join(emb_all_categs), inline = False)

        return embed



class CategoryArtistManagement(CmdCategory):
    """Artist management."""
    name = "artist management"

class CategoryBasics(CmdCategory):
    """Basic commands."""
    name = "basic commands"

class CategoryBotControl(CmdCategory):
    """Commands relating to bot control."""
    name = "bot control"

class CategoryModeration(CmdCategory):
    """Commands for moderating."""
    name = "moderation"
