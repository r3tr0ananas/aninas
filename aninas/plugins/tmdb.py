from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

import disnake
import disnake_plugins
from disnake.ext import commands

from ..constant import Emojis
from ..utils.embed import line_fix
from ..utils.tmdb import TMDb
from ..utils.types.tmdb.movie import Movie
from ..utils.types.tmdb.person import Person
from ..utils.types.tmdb.search import Search
from ..utils.types.tmdb.tv import TV

plugin = disnake_plugins.Plugin()

@plugin.load_hook()
async def load_tmdb():
    global tmdb
    tmdb = TMDb(plugin.bot.redis)

class TMDbDropdown(disnake.ui.StringSelect):
    def __init__(self, results: List[Search], author: disnake.User):
        self.results = results
        self.author = author

        options = self.get_options()

        super().__init__(
            placeholder="Choose option",
            min_values=1,
            max_values=1,
            options=options,
        )
    
    def get_options(self):
        options = []

        for result in self.results:
            value = f"{result['id']},{result['type']}"
            options.append(
                disnake.SelectOption(
                    label = result["name"],
                    value = value,      
                    description = result["description"][:60],
                )
            )
        
        return options  
    
    async def callback(self, inter: disnake.MessageInteraction) -> None:
        if self.author.id != inter.author.id:
            return await inter.response.send_message("You are not allowed to press this button", ephemeral=True)

        await inter.response.defer()

        data = self.values[0].split(",")

        metadata = await tmdb.get(data)

        if isinstance(metadata, Person):
            embed = person_embed(metadata)
        else:
            embed = media_embed(metadata)
        
        await inter.edit_original_response(embed=embed)

class DropDownView(disnake.ui.View):
    def __init__(self, results: List[Search], author: disnake.User):
        super().__init__(timeout=None)

        self.add_item(TMDbDropdown(results, author))

@plugin.slash_command(name="tmdb")
async def tmdb_command(inter):
    pass

@tmdb_command.sub_command(description="Search something on TMDb")
async def search(
    inter: disnake.CommandInteraction,
    query: str = commands.Param(description="Query")
):
    await inter.response.defer()

    results = await tmdb.search(query)
    view = DropDownView(results, inter.author)

    metadata = await tmdb.get(
        (
            results[0]["id"], 
            results[0]["type"]
        )
    )

    if isinstance(metadata, Person):
        embed = person_embed(metadata)
    else:
        embed = media_embed(metadata)

    await inter.followup.send(embed=embed, view=view)

@search.autocomplete("query")
async def query_complete(inter, query: str):
    return await tmdb.auto_comp(query)      

def person_embed(metadata: Person) -> disnake.Embed:
    name = metadata.name

    embed = disnake.Embed(
        title = name,
        description = metadata.bio
    )   

    embed.set_thumbnail(metadata.image)

    embed.url = metadata.url

    return embed

def media_embed(metadata: Movie | TV) -> disnake.Embed:
    name = metadata.name
    airtime_string = ""

    if isinstance(metadata, Movie):
        airtime_string = "- Release date: Not announced"
        if metadata.date:
            timestamp = int(metadata.date.timestamp())

            airtime_string = f"- Release date: <t:{timestamp}:d>"

    if metadata.name != metadata.original_name:
        name = f"{metadata.name} ({metadata.original_name})"

    embed = disnake.Embed(
        title = name,
        description = metadata.overview
    )

    embed.add_field(f"{Emojis.information} Info", 
        line_fix(
            f"""
            - Type: `{metadata.__class__.__name__}`
            - Genres: {" | ".join(metadata.genres)}
            - Status: `{metadata.status}`
            {airtime_string}
            """
        ),
        inline=False
    )

    if isinstance(metadata, TV):
        first_air_date = (
            f"<t:{int(metadata.first_date.timestamp())}:d>" 
            if metadata.first_date else "TBA"
        )
        last_air_date = (
            f"<t:{int(metadata.last_date.timestamp())}:d>" 
            if metadata.first_date else "Didn't start yet"
        )
        next_air_date = (
            f"<t:{int(metadata.next_date.timestamp())}:d>" 
            if metadata.next_date else ("Not set/Show ended" if metadata.first_date else "No idea")
        )

        embed.add_field(f"{Emojis.tv} Show Info", 
        line_fix(
            f"""
            - Seasons: `{metadata.seasons}`
            - Episodes: `{metadata.episodes}`
            - First air date: {first_air_date}
            - Last air date: {last_air_date}
            - Next air date: {next_air_date}
            """
        )   
    )

    embed.set_thumbnail(metadata.image)

    embed.url = metadata.url

    return embed

setup, teardown = plugin.create_extension_handlers()