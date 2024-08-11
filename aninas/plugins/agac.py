import disnake
from disnake.ext import plugins, commands
import disnake.http
import httpx

from ..constant import AGAC_URL

http_client = httpx.AsyncClient()
plugin = plugins.Plugin()

@plugin.slash_command()
async def agac(inter: disnake.CommandInteraction):
    pass

@agac.sub_command(description="Get a random image from anime-girls-and-computers")
async def random(inter: disnake.CommandInteraction):
    await inter.response.defer()

    async with http_client as client:
        request = await client.get(f"{AGAC_URL}/random")
        id = request.headers.get("x-image-id")

        metadata = await client.get(f"{AGAC_URL}/get/{id}/metadata")
        metadata = metadata.json()

    authors = [f"[{author['name']}](https://github.com/{author['github']})" for author in metadata["authors"]]

    embed = disnake.Embed(
        title = metadata["name"], 
        description = 
        f"""
        ## Metadata
        - **Category**: {metadata["category"]}
        - **Authors**: {", ".join(authors)}
        """,
        color=0xDE3163
    )

    embed.set_image(url=f"{AGAC_URL}/get/{id}")
    
    embed.set_footer(
        text="Brought to you by https://github.com/r3tr0ananas/agac-api"
    )

    await inter.followup.send(embed=embed)

@agac.sub_command(description="Search for image from anime-girls-and-computers")
async def search(
    inter: disnake.CommandInteraction,
    query: str     
):
    await inter.response.defer()

    async with http_client as client:
        request = await client.get(f"{AGAC_URL}/search?query={query}")
        data = request.json()

        if data == []:
            embed = disnake.Embed(
                title = "ImageNotFound", 
                description = "No image found based on your query 😔",
                color=0xDC143C
            )

            await inter.followup.send(embed=embed)
            return

        metadata = data[0]

    authors = [f"[{author['name']}](https://github.com/{author['github']})" for author in metadata["authors"]]

    embed = disnake.Embed(
        title = metadata["name"], 
        description = 
        f"""
        ## Metadata
        - **Category**: `{metadata["category"]}`
        - **Authors**: {", ".join(authors)}
        """,
        color=0xDE3163      
    )

    embed.set_image(url=f"{AGAC_URL}/get/{metadata['id']}")
    
    embed.set_footer(
        text="Brought to you by https://github.com/r3tr0ananas/agac-api"
    )

    await inter.followup.send(embed=embed)

@search.autocomplete("query")
async def query_autocomp(inter: disnake.ApplicationCommandInteraction, query: str):
    comps = []

    async with http_client as client:
        request = await client.get(f"{AGAC_URL}/search?query={query}")

    for item in request.json():
        comps.append(item["name"])

    return comps

setup, teardown = plugin.create_extension_handlers()