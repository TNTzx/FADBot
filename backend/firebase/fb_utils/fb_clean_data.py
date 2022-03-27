"""Functions for cleaning the data."""


def list_to_dict(list_: list):
    """Returns a dictionary with `{idx: item}`."""
    return {idx: item for idx, item in enumerate(list_)}
