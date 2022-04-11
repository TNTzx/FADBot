"""Contains functions for pretty printing."""


def pr_print(value, tab_ch = '\t', newline_char = '\n', indent = 0):
    """Returns a string for pretty logging."""
    prefix_char = newline_char + tab_ch * (indent + 1)
    if isinstance(value, dict):
        items = [
            prefix_char + repr(key) + ": " + pr_print(value[key], tab_ch, newline_char, indent + 1)
            for key in value
        ]
        return ",".join(items) + newline_char + tab_ch * indent
    if isinstance(value, (list, tuple)):
        items = [
            prefix_char + pr_print(item, tab_ch, newline_char, indent + 1)
            for item in value
        ]
        return ",".join(items) + newline_char + tab_ch * indent

    return repr(value)
