import disnake
from disnake.ext import plugins, commands

from ..utils import agac as agac_utils
from ..types import AGAC

plugin = plugins.Plugin()

@plugin.slash_command()
async def agac(inter: disnake.CommandInteraction):
    pass

@agac.sub_command(description="Get a random image from anime-girls-and-computers")
@commands.cooldown(1, 3, commands.BucketType.user)
async def random(inter: disnake.CommandInteraction):
    await inter.response.defer()

    metadata = await agac_utils.get_random()

    embed = await makeEmbed(metadata)

    await inter.followup.send(embed=embed)

@agac.sub_command(description="Search for image from anime-girls-and-computers")
@commands.cooldown(1, 3, commands.BucketType.user)
async def search(
    inter: disnake.CommandInteraction,
    query: str     
):
    await inter.response.defer()

    metadata = await agac_utils.search(query)

    if metadata is None:
        embed = disnake.Embed(
            title = "ImageNotFound", 
            description = "No image found based on your query 😔",
            color=0xFF0000
        )

        await inter.followup.send(embed=embed)
        return


    embed = await makeEmbed(metadata)

    await inter.followup.send(embed=embed)

@search.autocomplete("query")
async def query_autocomp(inter: disnake.ApplicationCommandInteraction, query: str):
    return await agac_utils.autocomplete(query)

async def makeEmbed(metadata: AGAC) -> disnake.Embed:
    authors = [f"[{author.name}](https://github.com/{author.github})" for author in metadata.authors]

    embed = disnake.Embed(
        title = metadata.name, 
        description = 
        f"""
        ## Metadata
        - **Category**: `{metadata.category.capitalize()}`
        - **Authors**: {", ".join(authors)}
        """,            
        color=0xDE3163      
    )

    embed.set_image(url = metadata.image)
    
    embed.set_footer(
        text="Brought to you by https://github.com/r3tr0ananas/agac-api"
    )

    return embed

setup, teardown = plugin.create_extension_handlers()