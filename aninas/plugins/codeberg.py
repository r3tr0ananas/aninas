import disnake
from disnake.ext import plugins, commands
from datetime import datetime

from ..utils import codeberg as cb

plugin = plugins.Plugin()

@plugin.slash_command()
async def codeberg(inter: disnake.CommandInteraction):
    pass

@codeberg.sub_command(description="Search for a repo on Codeberg")
@commands.cooldown(1, 3, commands.BucketType.user)
async def repo(
    inter: disnake.CommandInteraction,
    user: str = commands.Param(description="Username"),
    repo: str = commands.Param(description="Repostiory")
):
    await inter.response.defer()

    data = await cb.get_repo(user, repo)

    if isinstance(data, str):
        embed = disnake.Embed(
            title = f"Error while requesting: {user}/{repo}",
            description = data,
            color=0xFF0000
        )

        await inter.followup.send(embed=embed)
        return      

    embed = disnake.Embed(
        description = 
        f"""### [{data.name}]({data.url})
        {data.description}
        """, 
        color=0xDE3163
    )

    embed.set_author(
        name = data.owner.username,
        url = data.owner.user_url,
        icon_url = data.owner.avatar
    )

    created_at = datetime.strptime(data.created_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y")
    last_pushed = datetime.strptime(data.updated_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y at %H:%M")

    embed.set_footer(text = f"⑂ {data.forks} • ⭐ {data.stars} | Created: {created_at} • Last Commit: {last_pushed}")

    await inter.followup.send(embed=embed)

@codeberg.sub_command(description="Search for a repo on Codeberg")
@commands.cooldown(1, 3, commands.BucketType.user)
async def user(
    inter: disnake.CommandInteraction,
    user: str = commands.Param(description="Username")
):
    await inter.response.defer()

    data, repo_amount = await cb.get_user(user)

    if isinstance(data, str):
        embed = disnake.Embed(
            title = f"Error while requesting: {user}",
            description = data,
            color=0xFF0000
        )

        await inter.followup.send(embed=embed)
        return      

    username = f"{data.full_name} (@{data.username})" if data.full_name != "" else f"{data.username}"

    if data.pronouns != "":
        username = f"{username} | {data.pronouns}"

    embed = disnake.Embed(
        description = 
        f"""### [{username}]({data.user_url})
        {data.description}
        """, 
        color=0xDE3163
    )

    embed.add_field(
        name = "Followers",
        value = f"[{data.followers}]({data.user_url}?tab=followers)"
    )

    embed.add_field(
        name = "Following",
        value = f"[{data.following}]({data.user_url}?tab=following)"
    )

    embed.add_field(
        name = "Total Repos",
        value = f"[{repo_amount}]({data.user_url}?tab=repositories)"
    )

    if data.orgs != []:
        embed.add_field(
            name = "Organizations",
            value = f" | ".join([f"[{org.username}]({org.user_url})" for org in data.joined_orgs])
        )

    if data.website != "":
        embed.add_field(
            name = "Website",
            value = data.website
        )

    embed.set_thumbnail(data.avatar)

    created = datetime.strptime(data.created, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y at %H:%M")

    embed.set_footer(text = f"Joined: {created}")

    await inter.followup.send(embed=embed)

setup, teardown = plugin.create_extension_handlers()