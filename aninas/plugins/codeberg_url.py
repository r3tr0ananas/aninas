from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import CodebergPI

from disnake.ext import plugins
from datetime import datetime   

import disnake
import re

from ..utils import codeberg, messages

plugin = plugins.Plugin()

# Taken from Monty Bot
CODEBERG_ISSUE_LINK_REGEX = re.compile(
    r"https?:\/\/codeberg.org\/(?P<org>[a-zA-Z0-9][a-zA-Z0-9\-]{1,39})\/(?P<repo>[\w\-\.]{1,100})\/"
    r"(?P<type>issues|pulls)\/(?P<number>[0-9]+)[^\s]*"
)

AUTOMATIC_REGEX = re.compile(
    r"((?P<org>[a-zA-Z0-9][a-zA-Z0-9\-]{1,39})\/)?(?P<repo>[\w\-\.]{1,100})#(?P<number>[0-9]+)"
)

EMOJIS = {
    "pulls_open": "<:pr_open:1272273151182503966>",
    "pulls_merged": "<:pr_merged:1272273030013390888>",
    "pulls_draft": "<:pr_draft:1272273013286375454>",
    "pulls_closed": "<:pr_closed:1272273006479147152>",
    "issues_open": "<:issues_open:1272272998820483144>",
    "issues_closed": "<:issues_closed:1272272990754836641>"
}

@plugin.listener("on_message")
async def message(message: disnake.Message):
    if message.author.bot:
        return
    
    issue_link = CODEBERG_ISSUE_LINK_REGEX.match(message.content)
    automatic = AUTOMATIC_REGEX.match(message.content)

    if issue_link:
        user = issue_link.group("org")
        repo = issue_link.group("repo")
        number = issue_link.group("number")

        data = await codeberg.get_pi(user, repo, number)

        if data is None:
            return
        
        embed = await make_embed(data)

        await message.channel.send(embed=embed)
        await messages.suppress_embeds(plugin, message)

    elif automatic:
        user = automatic.group("org")
        repo = automatic.group("repo")
        number = automatic.group("number")

        data = await codeberg.get_pi(user, repo, number)

        if data is None:
            return
        
        embed = await make_embed(data)

        await message.channel.send(embed=embed)

async def make_embed(data: CodebergPI) -> disnake.Embed:
    if data.type == "pulls":
        if data.state == "open" and data.draft == False:
            emoji = EMOJIS["pulls_open"]
            color = 0x87ab63
        elif data.state == "closed" and data.merged == True:
            emoji = EMOJIS["pulls_merged"]
            color = 0xb259d0
        elif data.state == "open" and data.draft == True:
            emoji = EMOJIS["pulls_draft"]
            color = 0x30363b
        else:
            emoji = EMOJIS["pulls_closed"]
            color = 0xcc4848
    else:
        if data.state == "open":
            emoji = EMOJIS["issues_open"]
            color = 0x87ab63
        elif data.state == "closed":
            emoji = EMOJIS["issues_closed"]
            color = 0xcc4848

    embed = disnake.Embed(
        description = 
        f"""### {emoji} [{data.title}]({data.html_url})
        {data.body}
        """,
        color = color
    )

    embed.set_author(
        name = data.owner.username,
        url = data.owner.user_url,
        icon_url = data.owner.avatar
    )

    if data.labels != []:
        embed.add_field(
            name = "Labels",
            value = " | ".join(data.labels)
        )

    created_at = datetime.strptime(data.created_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y %H:%M")

    embed.set_footer(text=f"Created: {created_at}")

    return embed

setup, teardown = plugin.create_extension_handlers()