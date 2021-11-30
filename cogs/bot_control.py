# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-argument
# pylint: disable=no-self-use
# pylint: disable=too-many-branches

import os
import sys

import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import functions.command_wrapper as c_w


class RestartKill(cmds.Cog):
    def __init__(self, bot: nx.Client):
        self.bot = bot

    @c_w.command(
        category=c_w.Categories.bot_control,
        description="Restarts the bot.",
        aliases=["sr"],
        guild_only=False,
        req_dev=True,
    )
    async def switchrestart(self, ctx):
        await ctx.send("Restarting bot...")
        for file in os.listdir(os.path.dirname(__file__)):
            if file.endswith(".py"):
                if file == "__init__.py":
                    continue
                new_file = f"{file[:-3]}"

                try:
                    self.bot.unload_extension(new_file)
                except cmds.errors.ExtensionNotLoaded:
                    continue
                self.bot.load_extension(new_file)
        await ctx.send("Restarted!")
        print("\n \n Restart break! -------------------------------------- \n \n")


    @c_w.command(
        category=c_w.Categories.bot_control,
        description="Shuts down the bot.",
        aliases=["sk"],
        guild_only=False,
        req_dev=True
    )
    async def switchkill(self, ctx):
        await ctx.send("Terminated bot.")
        await self.bot.logout()


    @c_w.command(
        category=c_w.Categories.bot_control,
        description=f"Like {vrs.CMD_PREFIX}restart, but hard.",
        aliases=["srh"],
        guild_only=False,
        req_dev=True
    )
    async def switchrestarthard(self, ctx):
        await ctx.send("Restart initiated!")
        print("\n \n Restart break! Hard! -------------------------------------- \n \n")
        args = ['python'] + [f"\"{sys.argv[0]}\""]
        os.execv(sys.executable, args)


    @c_w.command(
        req_dev=True,
        guild_only=False
    )
    async def test(self, ctx: cmds.Context):
        # ...hey, uhm, man, you doing alright? Make sure to take some breaks okay? You need it! - past you
        async def button_or_text():
            class Buttons(nx.ui.View):
                def __init__(self):
                    super().__init__()
                    self.value = None
                
                @nx.ui.button(label="exit", style=nx.ButtonStyle.green)
                async def exit(self, button: nx.ui.Button, interact: nx.Interaction):

                    self.stop()
        
            view = Buttons()
            await ctx.send("beans?", view=view)
            check = check = lambda msg: ctx.author.id == msg.author.id and isinstance(msg.channel, nx.channel.DMChannel)
            await vrs.global_bot.wait_for("message", check=check)
        
        await button_or_text()
        await ctx.send("end")

def setup(bot):
    """Sets the bot up."""
    bot.add_cog(RestartKill(bot))
