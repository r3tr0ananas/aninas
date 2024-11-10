import disnake

from disnake.ext import commands

import disnake_plugins

from ..utils import uwu

plugin = disnake_plugins.Plugin()


@plugin.message_command(name="uwuify this text")
@commands.cooldown(1, 3, commands.BucketType.member)
async def message_uwuify(
    inter: disnake.ApplicationCommandInteraction, message: disnake.Message
):
    embed = disnake.Embed(
        title="uwuified nya~", description=f"```{uwu.uwuify(message.content)}```"
    )

    await inter.response.send_message(embed=embed)


@plugin.slash_command(description="uwuify your text nya~")
@commands.cooldown(1, 3, commands.BucketType.member)
async def uwuify(inter: disnake.CommandInteraction, text: str):
    embed = disnake.Embed(
        title="uwuified nya~", description=f"```{uwu.uwuify(text)}```"
    )

    await inter.response.send_message(embed=embed)


setup, teardown = plugin.create_extension_handlers()
