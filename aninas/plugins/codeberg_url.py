from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

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

CODEBERG_RE = re.compile(
    r"https?:\/\/codeberg.org\/(?P<repo>[a-zA-Z0-9-]+\/[\w.-]+)\/src\/branch\/(?P<path>[^#>]+)(\?[^#>]+)?"
    r"(?:#L(?P<start_line>\d+)-L(?P<end_line>\d+))?"
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
    def __init__(self, data: CodebergPI | CodebergIC, author: disnake.User):
        super().__init__(timeout=None)

        self.data = data
        self.author = author

    @disnake.ui.button(emoji="⬆️", label="Show less", style=disnake.ButtonStyle.green)
    async def show_less(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.author.id == inter.author.id or inter.permissions.manage_messages:
            if len(self.data.body) <= LIMIT_CHAR:
                await inter.response.send_message("There is nothing to shorten", ephemeral=True)
                return

            embed = make_embed(self.data, True)

            await inter.response.edit_message(embed=embed, view=ShowMore(self.data, self.author))
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
    def __init__(self, data: CodebergPI | CodebergIC, author: disnake.User):
        super().__init__(timeout=None)

        self.data = data
        self.author = author
    
    @disnake.ui.button(emoji="⬇️", label="Show more", style=disnake.ButtonStyle.green)
    async def show_more(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.author.id == inter.author.id or inter.permissions.manage_messages:  
            embed = make_embed(self.data)

            await inter.response.edit_message(embed=embed, view=ShowLess(self.data, self.author))

    @disnake.ui.button(emoji="🗑️", style=disnake.ButtonStyle.red)
    async def delete(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.author.id == inter.author.id or inter.permissions.manage_messages:
            await inter.response.defer()
            await inter.delete_original_response()


@plugin.listener("on_message")
async def message(message: disnake.Message):
    if message.author.bot:
        return
    
    file = CODEBERG_RE.search(message.content)
    comment = CODEBERG_COMMENT_LINK_REGEX.search(message.content)
    regex_match = CODEBERG_ISSUE_LINK_REGEX.search(message.content) or AUTOMATIC_REGEX.search(message.content)

    if file:
        repo = file.group("repo")
        path = file.group("path")
        start_line = file.group("start_line")
        end_line = file.group("end_line")
    
        data = await codeberg.get_file(repo, path, start_line, end_line)

        if data is None:
            return        
        
        await message.channel.send(data)
        await messages.suppress_embeds(plugin.bot, message)

    elif comment:
        user = comment.group("org")
        repo = comment.group("repo")
        number = comment.group("number")
        comment = comment.group("comment_id")

        data = await codeberg.get_comment(user, repo, number, comment)

        if data is None:
            return
        
        embed = make_embed(data)
        view = ShowLess(data, message.author)

        await message.channel.send(embed=embed,  view=view)
        await messages.suppress_embeds(plugin.bot, message)

    elif regex_match:
        user = regex_match.group("org")
        repo = regex_match.group("repo")
        number = regex_match.group("number")

        data = await codeberg.get_pi(user, repo, number)

        if data is None:
            return
        
        embed = make_embed(data)
        view = ShowLess(data, message.author)

        await message.channel.send(embed=embed,  view=view)
        await messages.suppress_embeds(plugin.bot, message)


def make_embed(data: CodebergPI | CodebergIC, show_less = False) -> disnake.Embed:
    if isinstance(data, CodebergPI):
        if data.type == "pulls":
            if data.state == "open" and not data.draft:
                emoji = Emojis.pulls_open
                color = Colours.pulls_open
            elif data.state == "closed" and data.merged:
                emoji = Emojis.pulls_merged
                color = Colours.pulls_merged
            elif data.state == "open" and data.draft:
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

    body = data.body

    if show_less:
        if len(body) > LIMIT_CHAR:
            body = f"{body[:LIMIT_CHAR]}..."

    embed = disnake.Embed(
        title = f"Comment: [{data.issue.full_name}] {data.issue.title}",
        description = body,
        color = Colours.pulls_draft
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