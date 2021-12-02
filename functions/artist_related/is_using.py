"""Module that contains functions to check, add, and delete users using a command."""

import functions.databases.firebase.firebase_interaction as f_i

async def check_if_using_command(author_id: int):
    """Returns true if the user is using the command."""
    users_using = f_i.get_data(["artistData", "pending", "isUsingCommand"])
    return str(author_id) in list(users_using)

async def add_is_using_command(author_id: int):
    """Adds the user as one that is using the command."""
    f_i.append_data(["artistData", "pending", "isUsingCommand"], [str(author_id)])

async def delete_is_using_command(author_id: int):
    """Deletes the user as one that is using the command."""
    data = f_i.get_data(["artistData", "pending", "isUsingCommand"])
    try:
        data.remove(str(author_id))
    except ValueError:
        pass
    f_i.edit_data(["artistData", "pending"], {"isUsingCommand": data})
