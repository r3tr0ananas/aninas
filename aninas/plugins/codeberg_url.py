from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

from disnake.ext import plugins

from ..types import CodebergPI, CodebergIC
from ..constant import Emojis, Colours
from ..utils import codeberg, messages, ui

import disnake
import re

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
    
        view = ui.Delete(message.author)
        
        await message.channel.send(data, view=view)
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
        view = ui.Delete(message.author)
        
        if len(data.body) > LIMIT_CHAR:
            view = ui.ShowLess(data, message.author, make_embed)

        await message.channel.send(embed=embed, view=view)
        await messages.suppress_embeds(plugin.bot, message)

    elif regex_match:
        user = regex_match.group("org")
        repo = regex_match.group("repo")
        number = regex_match.group("number")

        data = await codeberg.get_pi(user, repo, number)

        if data is None:
            return

        embed = make_embed(data)

        view = ui.Delete(message.author)

        if len(data.body) > LIMIT_CHAR:
            view = ui.ShowLess(data, message.author, make_embed)

        await message.channel.send(embed=embed, view=view)
        await messages.suppress_embeds(plugin.bot, message)

def make_embed(data: CodebergPI | CodebergIC, show_less = False) -> disnake.Embed:
    if isinstance(data, CodebergPI):
        return make_long_embed(data, show_less)

    body = data.body

    if show_less:
        if len(body) > LIMIT_CHAR:
            body = f"{body[:LIMIT_CHAR]}..."

    embed = disnake.Embed(
        title = f"Comment: [{data.issue.full_name}] {data.issue.title}",
        description = body,
        color = Colours.pulls_draft,
        timestamp = messages.timestamp(data.created_at)
    )

    embed.url = data.html_url

    embed.set_author(
        name = data.owner.username,
        url = data.owner.user_url,
        icon_url = data.owner.avatar
    )

    embed.set_footer(text=f"Commented on")

    return embed

def make_long_embed(data: CodebergPI, show_less) -> disnake.Embed:
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
        title = f"{emoji} [{data.full_name}] #{data.id} {data.title}",
        description = body,
        color = color,
        timestamp = messages.timestamp(data.created_at) 
    )

    embed.url = data.html_url

    embed.set_author(
        name = data.owner.username,
        url = data.owner.user_url,
        icon_url = data.owner.avatar
    )

    if not show_less:
        if data.labels != []:
            embed.add_field(
                name = "Labels",
                value = " | ".join(data.labels)
            )
        
        if data.due_date is not None:
            due_date = int(messages.timestamp(data.due_date).timestamp())

            embed.add_field(
                name = "Due Date",
                value = f"<t:{due_date}>"
            )
        
        if data.milestone is not None:
            embed.add_field(
                name = "Milestone",
                value = data.milestone
            )

        if data.requsted_reviewers is not None:
            embed.add_field(
                name = "Requested Reviewers",
                value = " | ".join([f"[{user.username}]({user.user_url})" for user in data.requsted_reviewers])
            )

        if data.assginees is not None:
            embed.add_field(
                name = "Assignees",
                value = " | ".join([f"[{user.username}]({user.user_url})" for user in data.assginees])
            )

        if data.assets is not None:
            embed.set_image(
                data.assets
            )

    embed.set_footer(text=f"Created at")

    return embed

setup, teardown = plugin.create_extension_handlers()