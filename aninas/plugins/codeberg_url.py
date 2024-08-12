from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import CodebergPI, CodebergIC

from disnake.ext import plugins
from datetime import datetime
from ..constant import Emojis, Colours

import disnake
import re

from ..utils import codeberg, messages

plugin = plugins.Plugin()

# Taken from Monty Bot
CODEBERG_ISSUE_LINK_REGEX = re.compile(
    r"https?:\/\/codeberg.org\/(?P<org>[a-zA-Z0-9][a-zA-Z0-9\-]{1,39})\/(?P<repo>[\w\-\.]{1,100})\/"
    r"(?P<type>issues|pulls)\/(?P<number>[0-9]+)[^\s]*"
)

CODEBERG_COMMENT_LINK_REGEX = re.compile(
    r"https?:\/\/codeberg.org\/(?P<org>[a-zA-Z0-9][a-zA-Z0-9\-]{1,39})\/(?P<repo>[\w\-\.]{1,100})"
    r"\/(?P<type>issues|pulls)\/(?P<number>[0-9]+)\/?#issuecomment-(?P<comment_id>[0-9]+)[^\s]*"
)

AUTOMATIC_REGEX = re.compile(
    r"((?P<org>[a-zA-Z0-9][a-zA-Z0-9\-]{1,39})\/)?(?P<repo>[\w\-\.]{1,100})#(?P<number>[0-9]+)"
)

LIMIT_CHAR = 240

class ShowLess(disnake.ui.View):
    def __init__(self, data: CodebergPI, author: disnake.User, embed_func):
        super().__init__(timeout=None)

        self.data = data
        self.author = author
        self.embed_func = embed_func

    @disnake.ui.button(emoji="⬆️", label="Show less", style=disnake.ButtonStyle.green)
    async def show_less(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.author.id == inter.author.id or inter.permissions.manage_messages:
            if len(self.data.body) <= LIMIT_CHAR:
                await inter.response.send_message("There is nothing to shorten", ephemeral=True)
                return

            embed = await self.embed_func(self.data, True)

            await inter.response.edit_message(embed=embed, view=ShowMore(self.data, self.author, self.embed_func))
        else:
            await inter.response.send_message("You are not allowed to press this button", ephemeral=True)
    

    @disnake.ui.button(emoji="🗑️", style=disnake.ButtonStyle.red)
    async def delete(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.author.id == inter.author.id or inter.permissions.manage_messages:
            await inter.response.defer()
            await inter.delete_original_response()
        else:
            await inter.response.send_message("You are not allowed to press this button", ephemeral=True)

class ShowMore(disnake.ui.View):
    def __init__(self, data: CodebergPI, author: disnake.User, embed_func):
        super().__init__(timeout=None)

        self.data = data
        self.author = author
        self.embed_func = embed_func    
    
    @disnake.ui.button(emoji="⬇️", label="Show more", style=disnake.ButtonStyle.green)
    async def show_more(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.author.id == inter.author.id or inter.permissions.manage_messages:  
            embed = await self.embed_func(self.data)

            await inter.response.edit_message(embed=embed, view=ShowLess(self.data, self.author, self.embed_func))

    @disnake.ui.button(emoji="🗑️", style=disnake.ButtonStyle.red)
    async def delete(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.author.id == inter.author.id or inter.permissions.manage_messages:
            await inter.response.defer()
            await inter.delete_original_response()


@plugin.listener("on_message")
async def message(message: disnake.Message):
    if message.author.bot:
        return
    
    comment = CODEBERG_COMMENT_LINK_REGEX.match(message.content)
    regex_match = CODEBERG_ISSUE_LINK_REGEX.match(message.content) or AUTOMATIC_REGEX.match(message.content)

    if comment:
        user = comment.group("org")
        repo = comment.group("repo")
        number = comment.group("number")
        comment = comment.group("comment_id")

        data = await codeberg.get_comment(user, repo, number, comment)

        if data is None:
            return
        
        embed = await make_comment_embed(data)
        view = ShowLess(data, message.author, make_comment_embed)

        await message.channel.send(embed=embed, view=view)
        await messages.suppress_embeds(plugin.bot, message)

    elif regex_match:
        user = regex_match.group("org")
        repo = regex_match.group("repo")
        number = regex_match.group("number")

        data = await codeberg.get_pi(user, repo, number)

        if data is None:
            return
        
        embed = await make_embed(data)
        view = ShowLess(data, message.author, make_embed)

        await message.channel.send(embed=embed, view=view)

        if CODEBERG_ISSUE_LINK_REGEX.match(message.content):
            await messages.suppress_embeds(plugin.bot, message)

async def make_embed(data: CodebergPI, show_less = False) -> disnake.Embed:
    if data.type == "pulls":
        if data.state == "open" and data.draft == False:
            emoji = Emojis.pulls_open
            color = Colours.pulls_open
        elif data.state == "closed" and data.merged == True:
            emoji = Emojis.pulls_merged
            color = Colours.pulls_merged
        elif data.state == "open" and data.draft == True:
            emoji = Emojis.pulls_draft
            color = Colours.pulls_draft
        else:
            emoji = Emojis.pulls_closed
            color = Colours.pulls_closed
    else:
        if data.state == "open":
            emoji = Emojis.issues_open
            color = Colours.issues_open
        elif data.state == "closed":
            emoji = Emojis.issues_closed
            color = Colours.issues_closed   

    body = data.body    
    
    if show_less:
        if len(body) > LIMIT_CHAR:
            body = f"{body[:LIMIT_CHAR]}..."

    embed = disnake.Embed(
        title = f"{emoji} [{data.full_name}] {data.title}",
        description = body,
        color = color       
    )

    embed.url = data.html_url

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

async def make_comment_embed(data: CodebergIC, show_less = False) -> disnake.Embed:
    body = data.body
    
    if show_less:
        if len(body) > LIMIT_CHAR:
            body = f"{body[:LIMIT_CHAR]}..."

    embed = disnake.Embed(
        title = f"Comment: [{data.issue.full_name}] {data.issue.title}",
        description = body,
        color = 0x33393e
    )

    embed.url = data.html_url

    embed.set_author(
        name = data.owner.username,
        url = data.owner.user_url,
        icon_url = data.owner.avatar
    )

    created_at = datetime.strptime(data.created_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y %H:%M")

    embed.set_footer(text=f"Commented on: {created_at}")

    return embed

setup, teardown = plugin.create_extension_handlers()