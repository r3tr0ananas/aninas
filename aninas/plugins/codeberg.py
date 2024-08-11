import disnake
from disnake.ext import plugins, commands
import httpx
from datetime import datetime

from ..constant import CODEBERG, CODEBERG_KEY
from ..types import CodebergRepo, CodebergUser

plugin = plugins.Plugin()
client = httpx.AsyncClient(headers={"Authorization": f"token {CODEBERG_KEY}"})

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

    request = await client.get(f"{CODEBERG}/repos/{user}/{repo}")
    data = request.json()

    if "errors" in data:
        error_message = data["errors"][0]

        embed = disnake.Embed(
            title = f"Error while requesting: {user}/{repo}",
            description = f"{error_message}",
            color=0xFF0000
        )

        await inter.followup.send(embed=embed)
        return

    data = CodebergRepo(data)

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

    request = await client.get(f"{CODEBERG}/users/{user}")
    data = request.json()

    if "message" in data:
        error_message = data["message"]

        embed = disnake.Embed(
            title = f"Error while requesting: {user}",
            description = f"{error_message}",
            color=0xFF0000
        )

        await inter.followup.send(embed=embed)
        return

    request_orgs = await client.get(f"{CODEBERG}/users/{user}/orgs")
    request_repos = await client.get(f"{CODEBERG}/users/{user}/repos")

    orgs_data = request_orgs.json()
    repos_data = request_repos.json()

    data = CodebergUser(data = data, orgs = orgs_data)

    username = f"{data.full_name} (@{data.username})" if data.full_name != "" else data.username

    if data.pronouns != "":
        username = f"{username} | {data.pronouns}"

    embed = disnake.Embed(
        description = 
        f"""### [{username}]({data.user_url})
        ```{data.description}```
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
        value = f"[{len(repos_data)}]({data.user_url}?tab=repositories)"
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