# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=useless-super-delegation
# pylint: disable=unused-import
# pylint: disable=invalid-name

class LogType:
    """Base class for defining logging structures."""
    def __init__(self, datas: ArtistStructures.Default):
        self.datas = datas

    class LogContainer:
        """Class that contains structure for logs."""
        class IDs:
            """Stores IDs."""
            def __init__(self):
                self.message_embed = self.MessageIDs()
                self.message_proof = self.MessageIDs()

            class MessageIDs:
                """Stores IDs that refer to a message."""
                def __init__(self, channel_id: int = None, message_id: int = None):
                    self.channel_id = str(channel_id)
                    self.message_id = str(message_id)

            def get_dict(self):
                """Gets dict."""
                return o_f.get_dict_attr(self)

        class Objects:
            """Stores channel and message objects."""
            def __init__(self, id_object: LogType.LogContainer.IDs | None):
                def get_message_from_ids(message_id_object: LogType.LogContainer.IDs.MessageIDs):
                    channel_obj: nx.TextChannel = vrs.global_bot.get_channel(int(message_id_object.channel_id))
                    return channel_obj.fetch_message(int(message_id_object.message_id))
                self.message_embed = get_message_from_ids(id_object.message_embed)
                self.message_proof = get_message_from_ids(id_object.message_proof)


    def get_channels(self, paths) -> list[nx.TextChannel]:
        """Get channels from firebase path.
        {"tag": "pa server", "channel": int}"""
        paths = f_i.get_data(paths)
        channels = []
        for entry in paths:
            try:
                channels.append(vrs.global_bot.get_channel(int(entry["channel"])))
            except TypeError:
                pass
        return channels

    def post_logs_firebase(self, _type: o_f.Unique):
        """Posts logs on discord then puts the message links on firebase."""
        if _type == self.LoggingTypes.PENDING:
            ArtistStructures.Firebase.Send.Pending(self.datas).send_logs()
        elif _type == self.LoggingTypes.EDITING:
            ArtistStructures.Firebase.Send.Editing(self.datas).send_logs()

    class LoggingTypes:
        """Class that contains logging types, like pending or editing."""
        PENDING = o_f.Unique()
        EDITING = o_f.Unique()

    async def post_logs_discord_base(self, _type: o_f.Unique, paths: list[str], post_to_firebase=False):
        """Post logs to discord."""
        if _type == self.LoggingTypes.PENDING:
            message_intro = "A new pending artist submission has been added. Here are the current details:"
        elif _type == self.LoggingTypes.EDITING:
            message_intro = "A new edit submission has been added. Here are the current details:"

        def store_message_id(message_obj: nx.Message):
            return LogType.LogContainer.IDs.MessageIDs(message_obj.channel.id, message_obj.id)

        messages: list[self.LogContainer] = []
        for channel_obj in self.get_channels(paths):
            log = self.LogContainer.IDs()
            log.message_embed = store_message_id(await channel_obj.send(message_intro, embed=await self.datas.generate_embed()))
            log.message_proof = store_message_id(await channel_obj.send(self.datas.proof))
            messages.append(log.get_dict())
        self.datas.discord_info.logs = messages

        if post_to_firebase:
            self.post_logs_firebase(_type)

    async def post_logs_discord(self, _type: o_f.Unique):
        """Inherited function."""

class LogStructures:
    """Contains log structures."""
    class Dump(LogType):
        """Type where messages aren't deleted."""
        async def post_logs_discord(self, _type: o_f.Unique):
            await self.post_logs_discord_base(_type, ["logData", "dump"])

    class Live(LogType):
        """Type where messages are deleted."""
        async def post_logs_discord(self, _type: o_f.Unique):
            await self.post_logs_discord_base(_type, ["logData", "live"], post_to_firebase=True)