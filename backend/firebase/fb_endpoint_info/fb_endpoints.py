"""All Firebase endpoints."""


from . import fb_endpoint as endpoint


class Root(endpoint.FBEndpointRoot):
    """The root."""
    def __init__(self):
        super().__init__()

        self.e_main_data = self.MainData(self)
        self.e_artist_data = self.ArtistData(self)
        self.e_discord_data = self.DiscordData(self)
        self.e_test = self.Test(self)


    class MainData(endpoint.FBEndpointParent):
        """Main variables. Used for stuff like getting the dev list."""
        def __init__(self, parent: endpoint.FBEndpoint):
            super().__init__(name = "main_data", parent = parent)

            self.e_privileges = self.Privileges(self)


        class Privileges(endpoint.FBEndpointParent):
            """Contains the privileges of each user / server."""
            def __init__(self, parent: endpoint.FBEndpoint):
                super().__init__(name = "privileges", parent = parent)

                self.e_devs = self.Devs(self)

            class Devs(endpoint.FBEndpointEnd):
                """Contains the IDs of developers."""
                def __init__(self, parent: endpoint.FBEndpoint):
                    super().__init__(name = "devs", parent = parent)


    class ArtistData(endpoint.FBEndpointParent):
        """Data relating to artists."""
        def __init__(self, parent: endpoint.FBEndpoint):
            super().__init__(name = "artist_data", parent = parent)

            self.e_change_req = self.ChangeReq(self)


        class ChangeReq(endpoint.FBEndpointParent):
            """Change request storage."""
            def __init__(self, parent: endpoint.FBEndpoint):
                super().__init__(name = "change_request", parent = parent)

                self.e_change_requests = self.ChangeRequests(self)
                self.e_can_verify = self.CanVerify(self)


            class ChangeRequests(endpoint.FBEndpointParent):
                """Contains the change requests."""
                def __init__(self, parent: endpoint.FBEndpoint):
                    super().__init__(name = "change_requests", parent = parent)


            class CanVerify(endpoint.FBEndpointParent):
                """Contains data for who can verify change requests."""
                def __init__(self, parent: endpoint.FBEndpoint):
                    super().__init__(name = "can_verify", parent = parent)

                class ServerRoles(endpoint.FBEndpointParent):
                    """Contains a list of servers and a list of their roles that have the privilege of being able to verify."""


    class DiscordData(endpoint.FBEndpointParent):
        """Contains Discord-related data."""
        def __init__(self, parent: endpoint.FBEndpoint):
            super().__init__(name = "discord_data", parent = parent)

            self.e_command_data = self.CommandData(self)
            self.e_guild_data = self.GuildData(self)
            self.e_user_general_data = self.UserGeneralData(self)


        class CommandData(endpoint.FBEndpointParent):
            """Data relating to commands."""
            def __init__(self, parent: endpoint.FBEndpoint):
                super().__init__(name = "command_data", parent = parent)

                self.e_is_using_command = self.IsUsingCommand(self)


            class IsUsingCommand(endpoint.FBEndpointParent):
                """Storage for the `is_using` implementation for commands."""
                def __init__(self, parent: endpoint.FBEndpoint):
                    super().__init__(name = "is_using_command", parent = parent)


        class GuildData(endpoint.FBEndpointParent):
            """Contains guild-specific data."""
            def __init__(self, parent: endpoint.FBEndpoint):
                super().__init__(name = "guild_data", parent = parent)


        class UserGeneralData(endpoint.FBEndpointParent):
            """Contains general user data, such as bans."""
            def __init__(self, parent: endpoint.FBEndpoint):
                super().__init__(name = "user_general_data", parent = parent)

                self.e_banned_users = self.BannedUsers(self)


            class BannedUsers(endpoint.FBEndpointParent):
                """Contains a list of banned users."""
                def __init__(self, parent: endpoint.FBEndpoint):
                    super().__init__(name = "banned_users", parent = parent)


    class Test(endpoint.FBEndpointParent):
        """Used for testing."""
        def __init__(self, parent: endpoint.FBEndpoint):
            super().__init__(name = "test", parent = parent)


ENDPOINTS = Root()
