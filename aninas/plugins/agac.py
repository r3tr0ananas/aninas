import disnake
from disnake.ext import plugins, commands
import disnake.http
import httpx

from ..constant import AGAC_URL
from ..types.agac import AGAC

client = httpx.AsyncClient()
plugin = plugins.Plugin()

@plugin.slash_command()
async def agac(inter: disnake.CommandInteraction):
    pass

@agac.sub_command(description="Get a random image from anime-girls-and-computers")
@commands.cooldown(1, 3, commands.BucketType.user)
async def random(inter: disnake.CommandInteraction):
    await inter.response.defer()

    request = await client.get(f"{AGAC_URL}/random")
    id = request.headers.get("x-image-id")

    metadata = await client.get(f"{AGAC_URL}/get/{id}/metadata")
    metadata = AGAC(metadata.json())

    embed = await makeEmbed(metadata)

    await inter.followup.send(embed=embed)

@agac.sub_command(description="Search for image from anime-girls-and-computers")
@commands.cooldown(1, 3, commands.BucketType.user)
async def search(
    inter: disnake.CommandInteraction,
    query: str     
):
    await inter.response.defer()

    request = await client.get(f"{AGAC_URL}/search?query={query}")
    data = request.json()

    if data == []:
        embed = disnake.Embed(
            title = "ImageNotFound", 
            description = "No image found based on your query 😔",
            color=0xFF0000
        )

        await inter.followup.send(embed=embed)
        return

    metadata = AGAC(data[0])

    embed = await makeEmbed(metadata)

    await inter.followup.send(embed=embed)

@search.autocomplete("query")
async def query_autocomp(inter: disnake.ApplicationCommandInteraction, query: str):
    comps = []

    request = await client.get(f"{AGAC_URL}/search?query={query}")

    for item in request.json():
        comps.append(item["name"])

    return comps

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

    embed.set_image(url=f"{AGAC_URL}/get/{metadata.id}")
    
    embed.set_footer(
        text="Brought to you by https://github.com/r3tr0ananas/agac-api"
    )

    return embed

setup, teardown = plugin.create_extension_handlers()