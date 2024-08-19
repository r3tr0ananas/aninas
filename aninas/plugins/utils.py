from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

from disnake.ext import commands, plugins

import disnake
import random
import base64

from ..constant import Emojis
from ..utils.embed import line_fix

from platform import python_version
from disnake import __version__ as disnake_version
from .. import __version__ as bot_version

plugin = plugins.Plugin()
HTTP_STATUS_CODES = [
    100, 101, 102, 103,
    200, 201, 202, 203, 204, 205, 206, 207, 208, 214, 226,
    300, 301, 302, 303, 304, 305, 307, 308,
    400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 
    414, 415, 416, 417, 418, 420, 421, 422, 423, 424, 425, 426, 428, 429, 431
]

@plugin.slash_command(description="Status about aninas")
async def status(
    inter: disnake.CommandInteraction
):
    embed = disnake.Embed(
        title = "Status",
        description = "Source: [Codeberg](https://codeberg.org/bananas/aninas)"
    )

    embed.add_field(
        f"{Emojis.zap} __Version__",
        line_fix(f"""
        - Python: `{python_version()}`
        - Disnake: `{disnake_version}`
        - Aninas: `{bot_version}`
        """)
    )

    embed.add_field(
        f"{Emojis.notepad} __Stats__",
        line_fix(f"""
        - Guilds: `{len(plugin.bot.guilds)}`
        - Uptime: <t:{plugin.bot.started}:R>
        """)
    )

    embed.set_author(
        name = "Ananas",
        url = "https://ananas.moe",
        icon_url = "https://avatars.githubusercontent.com/u/132799819"
    )

    embed.set_image(
        "https://cdn.ananas.moe/mashiro_shiina.png"
    )

    embed.set_footer(text = "uwu" if random.randint(1, 5) == 4 else "")

    await inter.response.send_message(embed=embed)

@plugin.slash_command(description="Get a image from http.cat")
async def httpcat(
    inter: disnake.CommandInteraction,
    status_code: int = commands.Param(description="HTTP status code")
):
    if status_code not in HTTP_STATUS_CODES:
        await inter.response.send_message("That is not a valid status code", ephemeral=True)
        return

    await inter.response.send_message(f"https://http.cat/{status_code}")

@plugin.slash_command(name="base64")
async def base64_command(inter):
    pass

@base64_command.sub_command(description="Encode something in base64")
@commands.cooldown(1, 3, commands.BucketType.user)
async def encode(
    inter: disnake.CommandInteraction,
    text: str = commands.Param(description="Your text to encode")
):
    text_bytes = bytes(text, "utf-8")

    encoded = base64.b64encode(text_bytes).decode()

    await inter.response.send_message(f"```{encoded}```")

@base64_command.sub_command(description="Decode something from base64")
@commands.cooldown(1, 3, commands.BucketType.user)
async def decode(
    inter: disnake.CommandInteraction,
    text: str = commands.Param(description="Your text to decode")
):
    try:
        decoded = base64.b64decode(text).decode()
    except:
        raise Exception("Invalid base64 string")

    if decoded.startswith("`"):
        decoded = "\u200b" + decoded

    decoded = decoded.replace("`", "`\u200b")

    await inter.response.send_message(f"```{decoded}```")

setup, teardown = plugin.create_extension_handlers()