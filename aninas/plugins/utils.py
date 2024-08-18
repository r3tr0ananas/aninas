from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.types.anime_girls import AnimeGirl

from disnake.ext import commands, plugins

import disnake
import base64

plugin = plugins.Plugin()

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