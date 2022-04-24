"""Discord embed utilities."""


import nextcord as nx


INVISIBLE_CHAR = "_ _"

def make_horizontal_rule(rule_length: int = 14, left_text: str = ""):
    """Adds a field with a horizontal rule in the embed."""
    if len(left_text) > rule_length:
        raise ValueError(f"Left-aligned text has greater length than rule length (expected <{rule_length}, text length is {len(left_text)}).")

    rule = "-" * (rule_length - len(left_text))
    return f"`{left_text}{rule}`"


def make_horizontal_rule_field(embed: nx.Embed, rule_length: int = 14, left_text: str = ""):
    """Like `make_horizontal_rule`, but adds a field to an `Embed`."""
    embed.add_field(
        name = make_horizontal_rule(rule_length, left_text),
        value = INVISIBLE_CHAR,
        inline = False
    )
