from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

from disnake.ext import plugins, commands

import disnake
import udatetime

from ..constant import (
    Emojis,
    Colours, 
    LINK_REGEX, 
    CODEBERG_RE, 
    CODEBERG_COMMENT_LINK_REGEX, 
    CODEBERG_ISSUE_LINK_REGEX, 
    AUTOMATIC_REGEX, 
    LIMIT_CHAR
)

from ..utils.types.codeberg import Issue, Comment
from ..utils.codeberg import Codeberg
from ..utils.ui import Delete, ShowLess
from ..utils.messages import suppress_embeds

plugin = plugins.Plugin()

@plugin.load_hook(post=True)
async def set_codeberg():
    global codeberg
    codeberg = Codeberg(plugin.bot.redis)

@plugin.slash_command(name="codeberg")
async def codeberg_command(inter):
    pass

@codeberg_command.sub_command(description="Get user info from Codeberg")
@commands.cooldown(1, 3, commands.BucketType.member)
async def user(
    inter: disnake.CommandInteraction,
    username: str = commands.Param(description="Codeberg username")
):
    await inter.response.defer()

    user = await codeberg.get_user(username)
    
    username = f"{user.full_name} (@{user.username})" if user.full_name != "" else f"{user.username}"

    if user.pronouns != "":
        username = f"{username} | {user.pronouns}"

    embed = disnake.Embed(
        title = username,
        description = user.description,
        timestamp = udatetime.from_string(user.created)
    )

    embed.url = user.user_url


    embed.add_field(
        name = f"{Emojis.follow} Followers",
        value = f"[{user.followers}]({user.user_url}?tab=followers)"
    )

    embed.add_field(
        name = f"{Emojis.follow} Following",
        value = f"[{user.following}]({user.user_url}?tab=following)"
    )

    embed.add_field(
        name = f"{Emojis.repo} Total Repos",
        value = f"[{len(user.repositories)}]({user.user_url}?tab=repositories)"
    )

    if user.organizations is not None:
        embed.add_field(
            name = "Organizations",
            value = " | ".join([f"[{org.username}]({org.user_url})" for org in user.organizations])
        )

    if user.website != "":
        embed.add_field(
            name = f"{Emojis.link} Website",
            value = user.website
        )

    embed.set_thumbnail(user.avatar)

    embed.set_footer(text = "Account created")

    view = Delete(inter.author)

    await inter.followup.send(embed=embed, view=view)


@codeberg_command.sub_command(description="Search for a repo on Codeberg")
@commands.cooldown(1, 3, commands.BucketType.user)
async def repo(
    inter: disnake.CommandInteraction,
    username: str = commands.Param(description="Codeberg username"),
    repostiory: str = commands.Param(description="Codeberg repostiory")
):
    await inter.response.defer()

    repo = await codeberg.get_repository(username, repostiory)

    name = f"{Emojis.repo} {repo.name}"

    if repo.fork:
        name = f"{Emojis.fork} {repo.name}"

    if repo.archived:
        name = f"{name} [archived]"

    embed = disnake.Embed(
        title = name,
        description = repo.description,
        timestamp = udatetime.from_string(repo.created_at)
    )

    embed.url = repo.url

    embed.set_author(
        name = repo.owner.username,
        url = repo.owner.user_url,
        icon_url = repo.icon
    )

    embed.set_footer(text = f"{Emojis.fork_footer} {repo.forks} • {Emojis.star} {repo.stars} • {Emojis.eye} {repo.watchers} / Created")

@plugin.listener("on_message")
async def on_message(message: disnake.Message):
    if message.author.bot:
        return
 
    embeds = []
    urls = set(LINK_REGEX.findall(message.content))

    for url in urls:
        if len(embeds) == 3:
            break

        file = CODEBERG_RE.match(url)
        comment = CODEBERG_COMMENT_LINK_REGEX.match(url)
        regex_match = CODEBERG_ISSUE_LINK_REGEX.match(url) or AUTOMATIC_REGEX.match(url)

        if file:
            repo = file.group("repo")
            path = file.group("path")
            start_line = file.group("start_line")
            end_line = file.group("end_line")
            
            if start_line is None:
                return
        
            data = await codeberg.get_code(repo, path, start_line, end_line)

            if data is None:
                return  
        
            view = Delete(message.author)
            
            await message.channel.send(data, view=view)
            return await suppress_embeds(plugin.bot, message)

        elif comment:
            user_repo = comment.group("repo")
            number = comment.group("number")
            comment = comment.group("comment_id")

            data = await codeberg.get_comment(user_repo, number, comment)

            if data is None:
                return
            
            embed = make_embed(data)

            embeds.append((data, embed))

        elif regex_match:
            user_repo = regex_match.group("repo")
            number = regex_match.group("number")

            data = await codeberg.get_issue(user_repo, number)

            if data is None:
                return

            embed = make_embed(data)

            embeds.append((data, embed))
    
    view = Delete(message.author)

    if len(embeds) == 1:
        view = ShowLess(embeds[0][0], message.author, make_embed)

    if len(embeds):
        real_embeds = [embed[1] for embed in embeds]

        await message.channel.send(embeds=real_embeds, view=view)
        await suppress_embeds(plugin.bot, message)

def make_embed(data: Issue | Comment, show_less = False) -> disnake.Embed:
    if isinstance(data, Issue):
        return make_issue_embed(data, show_less)

    body = data.body

    if show_less:
        if len(body) > LIMIT_CHAR:
            body = f"{body[:LIMIT_CHAR]}..."

    embed = disnake.Embed(
        title = f"Comment: [{data.issue.full_name}] {data.issue.title}",
        description = body,
        color = Colours.pulls_draft,
        timestamp = udatetime.from_string(data.created_at)
    )

    embed.url = data.html_url

    embed.set_author(
        name = data.owner.username,
        url = data.owner.user_url,
        icon_url = data.owner.avatar
    )

    embed.set_footer(text="Commented on")

    return embed

def make_issue_embed(data: Issue, show_less = False) -> disnake.Embed:
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
        timestamp = udatetime.from_string(data.created_at) 
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
            due_date = int(udatetime.from_string(data.due_date).timestamp())

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

        if data.image is not None:
            embed.set_image(
                data.image
            )

    embed.set_footer(text="Created at")

    return embed

setup, teardown = plugin.create_extension_handlers()