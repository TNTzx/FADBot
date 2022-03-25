"""Has functions for converting `None` -> `NULL_DATA`."""


from . import fb_consts


def check_if_iterable(obj):
    """Checks if the object is an Iterable."""
    try:
        len(obj)
    except TypeError:
        return False

    return True

def is_empty_or_undef(json: dict | list | tuple | str, undef, iter_check = True):
    "Returns `True` if the JSON is empty (if `iter_check` is `True`) or the undefined value, `False` otherwise."
    if json == undef:
        return True

    if iter_check and check_if_iterable(json):
        if len(json) == 0:
            return True

        return False

    return False


def undef_conversion(json: dict | list | tuple | str, from_undef: None, to_undef: None, iter_check = True):
    """Converts an undefined value to another undefined value in a JSON."""
    def conv_dict(diction: dict):
        for key, value in diction.items():
            if is_empty_or_undef(value, from_undef):
                diction[key] = to_undef

            if iter_check and check_if_iterable(value):
                diction[key] = undef_conversion(value, from_undef, to_undef, iter_check)

        return diction

    def conv_list(list_: list):
        for idx, item in enumerate(list_):
            if is_empty_or_undef(item, from_undef):
                list_[idx] = to_undef

            if iter_check and check_if_iterable(item):
                list_[idx] = undef_conversion(item, from_undef, to_undef, iter_check)

        return list_

    def conv_tuple(tuple_: tuple):
        new_tuple = conv_list(list(tuple_))
        return tuple(new_tuple)

    def conv_str(string: str):
        if is_empty_or_undef(string, from_undef):
            return to_undef

        return string


    if is_empty_or_undef(json, from_undef):
        return to_undef
    if isinstance(json, dict):
        return conv_dict(json)
    if isinstance(json, list):
        return conv_list(json)
    if isinstance(json, tuple):
        return conv_tuple(json)
    if isinstance(json, str):
        return conv_str(json)


    return json
