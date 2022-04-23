"""Contains logic for storing message bundles."""


import backend.discord_utils as disc_utils
import backend.firebase as firebase


class MessageBundle(firebase.FBStruct):
    """Stores the information on both the embed and proof messages."""
    def __init__(self, message_pointer_embed: disc_utils.MessagePointer, message_pointer_proof: disc_utils.MessagePointer):
        self.message_pointer_embed = message_pointer_embed
        self.message_pointer_proof = message_pointer_proof


    def firebase_to_json(self):
        return {
            "message_pointer_embed": self.message_pointer_embed.firebase_to_json(),
            "message_pointer_proof": self.message_pointer_proof.firebase_to_json()
        }

    @classmethod
    def firebase_from_json(cls, json: dict | list):
        def pointer_from_json(key: str):
            return disc_utils.MessagePointer.firebase_from_json(json.get(key))

        return cls(
            message_pointer_embed = pointer_from_json("message_pointer_embed"),
            message_pointer_proof = pointer_from_json("message_pointer_proof")
        )


    def get_messages(self):
        """
        Gets the messages from this `InfoMessageBundle` as a tuple.
        `(message_embed, message_proof)`
        """
        return (self.message_pointer_embed, self.message_pointer_proof)


    async def delete_bundle(self):
        """Deletes this `InfoMessageBundle` from Discord."""
        for message in self.get_messages():
            await message.delete_message()
