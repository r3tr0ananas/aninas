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
    except disnake.Forbidden as e:
        return False
    return True

# https://github.com/onerandomusername/monty-python/blob/main/monty/utils/messages.py#L87
def _validate_url(match: re.Match[str], *, group: str | int = "url") -> str:
    """Given a match, ensure that it is a valid url per Discord rules."""
    link = match.group(group)
    if link.startswith("<"):
        new_match = DISCORD_CLIENT_URL_WRAPPED_REGEX.match(match.string, match.pos)
        if new_match:
            link = match.group()
        else:
            link = link[1:]

        link = link.split(">", 1)[0]

    elif link.endswith(")"):
        depth = -1
        for char in link[-2::-1]:
            if char == ")":
                depth -= 1
            elif char == "(":
                depth += 1
            if depth == 0:
                break
        else:
            link = link[:-1]

    return link

# https://github.com/onerandomusername/monty-python/blob/main/monty/utils/messages.py#L128
def extract_urls(content: str) -> Generator[str, None, None]:
    """Extract all client rendered urls from the provided message content."""
    pos = 0
    while pos < len(content):
        for regex in (DISCORD_CLIENT_NAMED_URL_REGEX, DISCORD_CLIENT_URL_REGEX):
            match: re.Match[str] = regex.match(content, pos)
            if match:
                break
        else:
            pos += 1
            continue
        link = _validate_url(match, group="url")
        yield link
        pos = match.start("url") + len(link)