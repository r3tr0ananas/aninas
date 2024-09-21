from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anmoku import Anime, Character

import disnake
from disnake.ext import commands

import disnake_plugins

from ..utils.mal import MAL
from ..utils.embed import line_fix
from ..constant import Emojis

plugin = disnake_plugins.Plugin()

@plugin.load_hook()
async def load_mal():
    global mal
    mal = MAL(plugin.bot.redis)

@plugin.slash_command(name="mal", description="Search for an Anime or Character on MAL")
@commands.cooldown(5, 2, commands.BucketType.member)
async def mal_command(
    inter: disnake.CommandInteraction,
    query: str,
    search_type: str = commands.Param("anime", description="What should be searched, defaults to anime.", choices=["anime", "character"])
):
    await inter.response.defer()

    if query.isdigit():
        if search_type == "character":
            data = await mal.get_character(query)

            embed = character_embed(data)
        else:
            data = await mal.get_anime(query)
                
            embed = anime_embed(data)
    
        return await inter.followup.send(embed=embed)

    if search_type == "character":
        data = await mal.search_character(query)

        for char in data: # why do i have to iter it 😭
            embed = character_embed(char)
            break
    else:
        data = await mal.search_anime(query)
                
        for anime in data:
            embed = anime_embed(anime)
            break
    
    await inter.followup.send(embed=embed)

@mal_command.autocomplete("query")
async def query_autocomp(_, query):
    animes = await mal.search_anime(query)

    return [item.title.default for item in animes]

def character_embed(data: Character) -> disnake.Embed:
    embed = disnake.Embed(
        title = data.name,
        description = data.about
    )

    if data.name.kanji:
        embed.title = f"{embed.title} ({data.name.kanji})"

    if len(embed.description) > 300:
        embed.description = embed.description[:300] + f"... [Read more]({data.url})"

    embed.url = data.url

    embed.add_field(
        name = "Nicknames",
        value = " | ".join(data.nicknames)
    )

    embed.set_thumbnail(
        data.image.url
    )

    return embed

def anime_embed(data: Anime) -> disnake.Embed:
    embed = disnake.Embed(
        title = data.title,
        description = data.data["data"]["synopsis"]
    )

    if len(embed.description) > 240:
        embed.description = embed.description[:240] + f"... [Read more]({data.url})"

    embed.url = data.url

    genres = [f"`{genre['name']}`" for genre in data.data["data"]["genres"]]

    embed.add_field(
        name = f"{Emojis.information} Info",
        value = line_fix(f"""
        - Type: `{data.type}`
        - Genres: {" | ".join(genres)}
        - Status: `{data.status.value}`
        """),
        inline=False
    )

    if data.type == "TV":
        first_air = (
            f"<t:{int(data.aired.from_.timestamp())}:d>" 
            if data.aired.from_ else "Unknown"
        )
        last_air = (
            f"<t:{int(data.aired.to.timestamp())}:d>" 
            if data.aired.to and data.aired.from_ != data.aired.to else f"`{data.status.value}`"
        )

        embed.add_field(
            name = f"{Emojis.tv} TV Info",
            value = line_fix(f"""
            - Episodes: `{data.episodes}`
            - First air date: {first_air}
            - Last air date: {last_air}
            """),
            inline=False
        )

    embed.set_thumbnail(
        data.image.url
    )

    return embed

setup, teardown = plugin.create_extension_handlers()