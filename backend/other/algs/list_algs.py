"""Contains list-related algorithms."""


def subtract_list(minuend: list, subtrahend: list):
    """Subtract two lists."""
    difference = [item for item in minuend if item not in subtrahend]
    if difference == minuend:
        raise ValueError("Unchanged list.")
    return difference
