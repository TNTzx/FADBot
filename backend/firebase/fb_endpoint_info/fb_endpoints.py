"""All Firebase endpoints."""


from .. import fb_consts
from . import fb_endpoint as endpoint


class Root(endpoint.FBEndpointRoot):
    """The root."""
    def __init__(self):
        super().__init__()

        self.e_main = self.MainData(self)
        self.e_artist = self.ArtistData(self)
        self.e_discord = self.DiscordData(self)
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

                self.e_ch_reqs = self.ChangeRequests(self)
                self.e_can_verify = self.CanVerify(self)


            class ChangeRequests(endpoint.FBEndpointEnd):
                """Contains the change requests."""
                def __init__(self, parent: endpoint.FBEndpoint):
                    super().__init__(name = "change_requests", parent = parent)


            class CanVerify(endpoint.FBEndpointParent):
                """Contains data for who can verify change requests."""
                def __init__(self, parent: endpoint.FBEndpoint):
                    super().__init__(name = "can_verify", parent = parent)

                    self.e_server_roles = self.ServerRoles(self)
                    self.e_users = self.Users(self)

                class ServerRoles(endpoint.FBEndpointEnd):
                    """Contains a list of servers and a list of their roles that have the privilege of being able to verify."""
                    def __init__(self, parent: endpoint.FBEndpoint):
                        super().__init__(name = "server_roles", parent = parent)

                class Users(endpoint.FBEndpointEnd):
                    """Contains a list of IDs of users that can verify."""
                    def __init__(self, parent: endpoint.FBEndpoint):
                        super().__init__(name = "users", parent = parent)


    class DiscordData(endpoint.FBEndpointParent):
        """Contains Discord-related data."""
        def __init__(self, parent: endpoint.FBEndpoint):
            super().__init__(name = "discord_data", parent = parent)

            self.e_commands = self.CommandData(self)
            self.e_guilds = self.GuildData(self)
            self.e_users_general = self.UserGeneralData(self)


        class CommandData(endpoint.FBEndpointParent):
            """Data relating to commands."""
            def __init__(self, parent: endpoint.FBEndpoint):
                super().__init__(name = "command_data", parent = parent)

                self.e_is_using = self.IsUsingCommand(self)


            class IsUsingCommand(endpoint.FBEndpointEnd):
                """Storage for the `is_using` implementation for commands."""
                def __init__(self, parent: endpoint.FBEndpoint):
                    super().__init__(name = "is_using_command", parent = parent)


        class GuildData(endpoint.FBEndpointEnd):
            """Contains guild-specific data."""
            def __init__(self, parent: endpoint.FBEndpoint):
                super().__init__(name = "guild_data", parent = parent)

            def get_default_data(self):
                return {
                    "admin_role": 0,
                    "logs": {
                        "locations": {
                            "dump": fb_consts.PLACEHOLDER_DATA,
                            "live": fb_consts.PLACEHOLDER_DATA
                        }
                    }
                }


        class UserGeneralData(endpoint.FBEndpointParent):
            """Contains general user data, such as bans."""
            def __init__(self, parent: endpoint.FBEndpoint):
                super().__init__(name = "user_general_data", parent = parent)

                self.e_banned_users = self.BannedUsers(self)


            class BannedUsers(endpoint.FBEndpointEnd):
                """Contains a list of banned users."""
                def __init__(self, parent: endpoint.FBEndpoint):
                    super().__init__(name = "banned_users", parent = parent)


    class Test(endpoint.FBEndpointParent):
        """Used for testing."""
        def __init__(self, parent: endpoint.FBEndpoint):
            super().__init__(name = "test", parent = parent)


ENDPOINTS = Root()


class ShortEndpoint():
    """Contains shortcuts for the endpoints."""
    devs = ENDPOINTS.e_main.e_privileges.e_devs

    artist_change_reqs = ENDPOINTS.e_artist.e_change_req.e_ch_reqs
    artist_can_verify = ENDPOINTS.e_artist.e_change_req.e_can_verify

    discord_cmds = ENDPOINTS.e_discord.e_commands
    discord_guilds = ENDPOINTS.e_discord.e_guilds
    discord_users_general = ENDPOINTS.e_discord.e_users_general

    test = ENDPOINTS.e_test
