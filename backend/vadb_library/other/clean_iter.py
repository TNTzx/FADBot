"""Cleans an iterable from empty iterables."""



def check_if_iterable(obj):
    """Checks if the object is an Iterable."""
    try:
        len(obj)
    except TypeError:
        return False

    return True


def check_if_not_empty(obj: dict | list | tuple | str):
    """Returns `False` if this iterable is empty, `True` otherwise. If it's not an iterable, return `True`."""

    if not check_if_iterable(obj):
        return True

    if isinstance(obj, str):
        if len(obj) > 0:
            return True
    elif isinstance(obj, (dict, list, tuple)):
        for item in obj:
            if check_if_not_empty(item):
                return True

    return False


def clean_iterable(obj: dict | list | tuple | str | None):
    """Returns None if the iterable and the iterables inside it is empty or has only None, else return the iterable that doesn't have blank stuff."""

    def clean_dict(dictionary: dict):
        new_dictionary = {}

        for key, value in dictionary.items():
            if check_if_iterable(value):
                new_value = clean_iterable(value)
                if new_value is not None:
                    new_dictionary[key] = new_value
            else:
                new_dictionary[key] = value

        if check_if_not_empty(new_dictionary):
            return new_dictionary

        return None


    def clean_list(list_: list):
        new_list = []

        for item in list_:
            if check_if_iterable(item):
                new_item = clean_iterable(item)
                if new_item is not None:
                    new_list.append(new_item)
            else:
                new_list.append(item)

        if check_if_not_empty(new_list):
            return new_list

        return None


    def clean_str(string: str):
        if check_if_not_empty(string):
            return string

        return None


    if obj is None:
        return None
    if isinstance(obj, dict):
        return clean_dict(obj)
    if isinstance(obj, list):
        return clean_list(obj)
    if isinstance(obj, tuple):
        result = clean_list(list(obj))
        if result is not None:
            return tuple(obj)

        return None
    if isinstance(obj, str):
        return clean_str(obj)


    raise ValueError(f"Object {obj} not dict, list, tuple, or str.")
