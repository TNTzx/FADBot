"""Contains a function for wrapping text."""


from . import prefixes


def wrap_text(
        text: str,
        max_length = 35,
        break_char: str = " ", separate_char: str = "\n",
        subseq_indent: prefixes.Indent = prefixes.Indent()
        ):
    """Wraps the text with a maximum char length."""
    def get_broken_parts(text_part: str):
        if len(text_part) <= max_length:
            return [text_part]

        text_subset = text_part[:max_length]

        if break_char in text_subset:
            target_char_idx = text_subset.rfind(break_char)
            target_char_idxs = (target_char_idx, target_char_idx + 1)
        else:
            target_char_idxs = (max_length, max_length)


        return [text_part[:target_char_idxs[0]]] + get_broken_parts(text_part[target_char_idxs[1]:])


    broken_parts = get_broken_parts(text)
    broken_parts_except_first = [f"{subseq_indent.get_str()}{part}" for part in broken_parts[1:]]
    broken_parts = [broken_parts[0]] + broken_parts_except_first

    return separate_char.join(broken_parts)
