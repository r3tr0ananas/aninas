from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

from disnake.ext import plugins
from datetime import datetime

import platform
import disnake

from .. import __version__ as bot_version
from ..utils.embeds import line_fix
from ..utils.stats import Stats

from disnake import __version__ as disnake_version
from ..constant import Emojis

plugin = plugins.Plugin()
stats = Stats()

BOT_START_TIME = int(datetime.now().timestamp())

@plugin.slash_command(description="Status of aninas")
async def status(inter: disnake.CommandInteraction):
    embed = disnake.Embed(
        title = "Status"
    )

    embed.add_field(
        f"{Emojis.notepad} __Stats__",
        line_fix(f"""
        - Uptime: <t:{BOT_START_TIME}:R>
        - Guilds: `{len(plugin.bot.guilds)}`
        """),
        inline  = False
    )

    embed.add_field(
        f"{Emojis.zap} __Version__",
        line_fix(f"""
        - aninas: `{bot_version}`
        - Disnake: `{disnake_version}`
        - Python: `{platform.python_version()}`
        """)    
    )

    embed.add_field(
        f"{Emojis.package} __Resources__",
        line_fix(f"""
        - Latency: `{int(plugin.bot.latency * 1000)}ms`
        - OS: `{platform.system()} {platform.release()}`
        - CPU: `{stats.cpu_usage}%`
        - RAM: `{stats.ram_usage} MB`
        """)
    )

    embed.set_author(
        name = "r3tr0ananas",
        icon_url = "https://avatars.githubusercontent.com/u/132799819",
        url = "https://ananas.moe"
    )

    embed.set_image("https://cdn.ananas.moe/mashiro_shiina.png")

    await inter.response.send_message(embed=embed)

@plugin.slash_command()
async def ping(
    inter: disnake.CommandInteraction
):
    now = datetime.now()

    await inter.response.send_message("Pong")

    elapsed_time = datetime.now() - now
    elapsed_ms = int(elapsed_time.total_seconds() * 1000)

    await inter.edit_original_response(f"Took {elapsed_ms}ms {Emojis.loading_cat}")

setup, teardown = plugin.create_extension_handlers()