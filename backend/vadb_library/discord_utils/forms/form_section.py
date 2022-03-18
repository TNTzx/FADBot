""""Contains logic for form sections."""


import abc
import typing as typ

import nextcord as nx
import nextcord.ext.commands as cmds

import backend.utils.views as vw
import backend.exceptions.send_error as s_e
import global_vars.variables as vrs

from . import section_states as states


async def check_response(ctx: cmds.Context, view: vw.View):
    """Checks the response of the user if they went back, cancelled, etc."""
    if view.value == vw.OutputValues.cancel:
        await s_e.cancel_command(ctx, send_author=True)
    elif view.value == vw.OutputValues.skip or:
        await ctx.author.send("Section skipped.")
    else:
        raise NotImplementedError("Not implemented response.")


class FormSection(abc.ABC):
    """A form section."""
    text_ext: str = None

    def __init__(
            self,
            title: str,
            description: str,
            required: bool,
            example: str = None,
            notes: str = None
            ):
        self.title = title
        self.description = description
        self.required = required
        self.example = example
        self.notes = notes


    def generate_embed(self, section_state: states.SectionState = states.SectionStates.default):
        """Generates the embed for this section."""
        def make_empty_field(embed: nx.Embed):
            """Makes an empty field on the embed."""
            embed.add_field(name="_ _", value="_ _", inline=False)

        if section_state == states.SectionStates.default:
            emb_title = self.title
        else:
            emb_title = f"{self.title} ({section_state.name})"

        embed = nx.Embed(color = vrs.COLOR_PA, title = emb_title)

        make_empty_field(embed)

        emb_req = f"You have to send {self.text_ext}!"

        emb_req_desc = []
        if self.example is not None:
            emb_req_desc.append((
                "__Here is an example of what you have to send:__\n"
                f"`{self.example}`"
            ))
        if self.notes is not None:
            emb_req_desc.append(f"__Note:__\n{self.notes}")

        embed.add_field(name = emb_req, value = "\n".join(emb_req_desc))

        make_empty_field(embed)

        embed.set_footer(text = section_state.footer)

        return embed

    

    def send_section(self, ctx: cmds.Context, section_state: states.SectionState = states.SectionStates.default, extra_view: typ.Type[vw.View] = vw.Blank):
        """Sends the section to the user then returns the output."""
        class ViewMerged(section_state.view_cls, extra_view):
            """Merged views."""
        
        while 


class ViewInput(FormSection):
    """A `FormSection` with a view input."""

class TextInput(FormSection):
    """A `FormSection` with a text input."""

    def reformat_text(self, text: str):
        """Reformats the text input."""


class NumberSection(TextInput):
    """A number section."""
    text_ext = "a number"

class RawTextSection(TextInput):
    """A text section."""
    text_ext = "some text"

class LinksSection(TextInput):
    """A links section."""
    text_ext = "some links"

class ImageSection(TextInput):
    """An image section."""
    text_ext = "an image"

class ListSection(TextInput):
    """A list section."""
    text_ext = "a list"

class DictSection(TextInput):
    """A dictionary section."""
    text_ext = "a dictionary"

class ChoiceSection(ViewInput):
    """A choice section."""
    text_ext = "a choice"



class FormSections():
    """Contains all form sections."""
    name = RawTextSection()
