from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

from disnake.ext import plugins

from ..utils import embeds

import base64 as b64
import disnake

plugin = plugins.Plugin()

@plugin.slash_command()
async def base64(inter):
    pass

@base64.sub_command()
async def decode(
    inter: disnake.CommandInteraction,
    text: str
):
    try:
        decoded = b64.b64decode(text).decode()
    except Exception as e:
        embed = embeds.error_embed("Base64 Error", e)
        
        await inter.response.send_message(embed=embed)
        return

    if decoded.startswith("`"):
        decoded = "\u200b" + decoded

    decoded = decoded.replace("`", "`\u200b")

    await inter.response.send_message(f"```{decoded}```")

@base64.sub_command()
async def encode(
    inter: disnake.CommandInteraction,
    text: str
):
    try:
        text_in_bytes = bytes(text, "utf-8")
        encoded = b64.b64encode(text_in_bytes).decode()
    except Exception as e:
        embed = embeds.error_embed("Base64 Error", e)
        
        await inter.response.send_message(embed=embed)
        return

    await inter.response.send_message(f"```{encoded}```")

setup, teardown = plugin.create_extension_handlers()