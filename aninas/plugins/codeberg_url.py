from disnake.ext import plugins, commands
from datetime import datetime

import disnake
import httpx
import re

from ..constant import CODEBERG, CODEBERG_KEY
from ..types import CodebergPI

plugin = plugins.Plugin()
client = httpx.AsyncClient(headers={"Authorization": f"token {CODEBERG_KEY}"})

# Taken from Monty Bot
CODEBERG_ISSUE_LINK_REGEX = re.compile(
    r"https?:\/\/codeberg.org\/(?P<org>[a-zA-Z0-9][a-zA-Z0-9\-]{1,39})\/(?P<repo>[\w\-\.]{1,100})\/"
    r"(?P<type>issues|pulls)\/(?P<number>[0-9]+)[^\s]*"
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
    
    regex_match = CODEBERG_ISSUE_LINK_REGEX.match(message.content)

    if not regex_match:
        return
    
    user = regex_match.group("org")
    repo = regex_match.group("repo")
    git_type = regex_match.group("type")
    number = regex_match.group("number")

    request = await client.get(f"{CODEBERG}/repos/{user}/{repo}/{git_type}/{number}")
    data = request.json()

    if "message" in data:
        return

    emoji = ""
    color = ""

    data = CodebergPI(data)

    if git_type == "pulls":
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
        color=color 
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

    await message.channel.send(embed=embed)

    await message.edit(suppress_embeds=True)

setup, teardown = plugin.create_extension_handlers()