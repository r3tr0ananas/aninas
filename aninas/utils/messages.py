from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Generator

import asyncio
import disnake
import re

from disnake.ext import commands

DISCORD_CLIENT_URL_REGEX = re.compile(r"(?P<url><?https?:\/\/[^\s<]+[^<.,:;'\"\]\s]\>?)", re.IGNORECASE)
DISCORD_CLIENT_URL_WRAPPED_REGEX = re.compile(r"(?<=\<)https?:\/\/[^\s>]+(?=\>)", re.IGNORECASE)
DISCORD_CLIENT_NAMED_URL_REGEX = re.compile(
    r"^\[(?P<title>(?:\[[^\]]*\]|[^\[\]]|\](?=[^\[]*\]))*)\]\(\s*(?P<url><?(?:\([^)]*\)|[^\s\\]|\\.)*?>?)(?:\s+['\"]([\s\S]*?)['\"])?\s*\)",
    re.IGNORECASE,
)

# https://github.com/onerandomusername/monty-python/blob/main/monty/utils/messages.py#L57
async def suppress_embeds(
    bot: commands.InteractionBot,
    message: disnake.Message,
    *,
    wait: Optional[float] = 6,
) -> bool:
    if not message.embeds:
        if wait is not None:
            try:
                _, message = await bot.wait_for("message_edit", check=lambda b, m: m.id == message.id, timeout=wait)
            except asyncio.TimeoutError:
                pass
            if not message.embeds:
                return False
            await asyncio.sleep(0.2)

    try:
        await message.edit(suppress_embeds=True)
    except disnake.NotFound:
        return False
    except disnake.Forbidden:
        return False
    return True