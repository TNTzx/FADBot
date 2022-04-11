"""Discord embed utilities."""


import nextcord as nx


INVISIBLE_CHAR = "_ _"

def make_horizontal_rule(embed: nx.Embed, rule_length: int = 14):
    """Adds a field with a horizontal rule in the embed."""
    hor_rule = "⎯" * rule_length
    embed.add_field(
        name = hor_rule,
        value = INVISIBLE_CHAR
    )
