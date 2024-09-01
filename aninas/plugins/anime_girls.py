from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.types.anime_girls import AnimeGirl

import disnake
from disnake.ext import commands, plugins

from ..utils.anime_girls import AnimeGirls
from ..utils.embed import line_fix

plugin = plugins.Plugin()

@plugin.load_hook()
async def load_anime_girls():
    global anime_girls
    anime_girls = AnimeGirls(plugin.bot.redis)

@plugin.slash_command()
async def agac(inter):
    pass

@agac.sub_command(description="Get a random anime girl from agac")
@commands.cooldown(1, 3, commands.BucketType.user)
async def random(
    inter: disnake.CommandInteraction
):
    await inter.response.defer()

    random_girl = await anime_girls.random()

    await inter.followup.send(embed=make_embed(random_girl))

@agac.sub_command(description="Search for a random anime girl from agac")
@commands.cooldown(1, 3, commands.BucketType.user)
async def search(
    inter: disnake.CommandInteraction,
    query: str = commands.Param(description="Query")
):
    await inter.response.defer()

    random_girl = await anime_girls.get(query)

    await inter.followup.send(embed=make_embed(random_girl))

@search.autocomplete("query")
async def query_autocomp(inter: disnake.ApplicationCommandInteraction, query: str):
    return await anime_girls.auto_comp(query)

def make_embed(data: AnimeGirl) -> disnake.Embed:
    authors = [f"[{author.name}](https://github.com/{author.github})" for author in data.authors]

    embed = disnake.Embed(
        title = data.name,
        description=line_fix(f"""
        - ID: `{data.id}`
        - Category: `{data.category}`
        - Authors: {" | ".join(authors)}
        """)
    )

    embed.set_image(data.image)

    return embed

setup, teardown = plugin.create_extension_handlers()