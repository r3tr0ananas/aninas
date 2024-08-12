from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

from disnake.ext import plugins
from datetime import datetime

import disnake

from .. import __version__ as bot_version
from disnake import __version__ as disnake_version

plugin = plugins.Plugin()

BOT_START_TIME = int(datetime.now().timestamp())

@plugin.slash_command()
async def status(inter: disnake.CommandInteraction):
    embed = disnake.Embed(
        title="Status",
        description=f"""
        Version: `{bot_version}`
        Disnake version: `{disnake_version}`

        Guilds: `{len(plugin.bot.guilds)}`
        
        Latency: `{int(plugin.bot.latency * 1000)}ms`
        Uptime: <t:{BOT_START_TIME}:R>
        """
    )

    embed.set_author(
        name = "r3tr0ananas",
        icon_url = "https://avatars.githubusercontent.com/u/132799819",
        url = "https://ananas.moe"
    )

    embed.set_image("https://cdn.ananas.moe/mashiro_shiina.png")

    await inter.response.send_message(embed=embed)

setup, teardown = plugin.create_extension_handlers()