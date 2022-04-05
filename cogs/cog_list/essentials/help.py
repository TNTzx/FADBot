"""Contains the help command."""


import nextcord as nx
import nextcord.ext.commands as cmds

import global_vars.variables as vrs
import backend.command_related.command_wrapper as c_w
import backend.other_functions as o_f
import backend.exceptions.send_error as s_e


class CogHelp(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c_w.command(
        category = c_w.Categories.basic_commands,
        description="WHAT IN THE ACTUAL LIVING ARTIST DID YOU DO",
        parameters={"[command]": "DID YOU SERIOUSLY NEED HELP ON A HELP COMMAND"},
        aliases=["h"],
        guild_only=False,
        cooldown=1, cooldown_type=cmds.BucketType.user
    )
    async def help(self, ctx: cmds.Context, command=None):
        async def show_all():
            embed = nx.Embed(
                title = "Help!",
                description=(
                    f"**Command Prefix: `{vrs.CMD_PREFIX}`**\n"
                    "This bot was made possible by Nao's website. Go check it out! [**VADB link**](https://fadb.live/)\n"
                    "This bot is created by //TNTz.\n\n"
                    "Use `##help <command>` to view help for that command!"
                ),
                color = 0xFFAEAE
            )
            for category, names in c_w.ListOfCommands.commands_all.items():

                name_list = []
                for name in names:
                    cmd = c_w.ListOfCommands.commands[name]
                    if cmd.help.show_condition(ctx) and cmd.help.show_help:
                        name_list.append(name)

                name_form = f"`{'`, `'.join(name_list)}`"
                embed.add_field(name=category, value=name_form, inline=False)
            await ctx.send(embed=embed)


        async def specific():
            async def send_not_exist():
                await s_e.send_error(ctx, "*This command doesn't exist! Make sure you typed it correctly!*")

            if not command in c_w.ListOfCommands.commands:
                await send_not_exist()
                return

            cmd: c_w.CustomCommandClass = c_w.ListOfCommands.commands[command]

            if not cmd.help.show_condition(ctx) or not cmd.help.show_help:
                await send_not_exist()
                return

            help_docs = cmd.help

            embed = nx.Embed(
                title=f"Help: {help_docs.category} // {vrs.CMD_PREFIX}{cmd.name}",
                color=0xFFAEAE
            )

            async def create_separator():
                separator = f"{'-' * 20}"
                embed.add_field(name=separator, value="_ _", inline=False)


            embed.add_field(name="Description", value=help_docs.description, inline=False)

            if len(help_docs.aliases) > 0:
                aliases = "`, `".join(help_docs.aliases)
                embed.add_field(name="Aliases:", value=f"`{aliases}`", inline=False)

            await create_separator()

            syntax_list = "> <".join(help_docs.parameters.keys())
            syntax_list = f" `<{syntax_list}>`" if syntax_list != "" else "_ _"
            embed.add_field(name="Syntax:", value=f"`{vrs.CMD_PREFIX}{cmd.name}`{syntax_list}", inline=False)

            if len(help_docs.parameters) > 0:
                params_list = "\n".join([f"`<{param}>`: {paramDesc}" for param, paramDesc in help_docs.parameters.items()])
                embed.add_field(name="Parameters:", value=f"{params_list}", inline=False)

            await create_separator()

            guild_only = "only in servers." if help_docs.guild_only else "in direct messages and servers."
            embed.add_field(name=f"Can be used {guild_only}", value="_ _", inline=False)

            require = help_docs.require
            if require.guild_owner or require.guild_admin or require.dev or require.pa_mod:
                requirements = []
                if require.pa_mod:
                    requirements.append("Project Arrhythmia Moderators")
                if require.guild_owner:
                    requirements.append("Server Owner")
                if require.guild_admin:
                    requirements.append("Server Owner / Admins")
                if require.dev:
                    requirements.append("Bot Developer")

                req_form = "`, `".join(requirements)

                embed.add_field(name="Only allowed for:", value=f"`{req_form}`")

            cooldown = help_docs.cooldown
            if cooldown.length > 0:
                if cooldown.type == cmds.BucketType.guild:
                    cooldown_type = "Entire server"
                elif cooldown.type == cmds.BucketType.member:
                    cooldown_type = "Per member"
                elif cooldown.type == cmds.BucketType.channel:
                    cooldown_type = "Per channel"
                elif cooldown.type == cmds.BucketType.category:
                    cooldown_type = "Per channel category"
                elif cooldown.type == cmds.BucketType.role:
                    cooldown_type = "Per role"
                elif cooldown.type == cmds.BucketType.user:
                    cooldown_type = "Per user"
                else:
                    cooldown_type = "TNTz messed up, he didn't add another edge case, please ping him"
                cooldown_form = (
                    f"Duration: `{o_f.format_time(help_docs.cooldown.length)}`\n"
                    f"Applies to: `{cooldown_type}`"
                )
                embed.add_field(name="Cooldown Info:", value=f"{cooldown_form}")

            if not len(help_docs.example_usage) == 0:
                example_usage_form = "`\n`".join(help_docs.example_usage)
                embed.add_field(name="Examples on How To Use:", value=f"`{example_usage_form}`", inline=False)

            await ctx.send(embed=embed)


        if command is None:
            await show_all()
        else:
            await specific()

def setup(bot: nx.Client):
    bot.add_cog(CogHelp(bot))
