import disnake
from disnake.ext import plugins
import httpx

from ..constant import SATA_ANDAGI

plugin = plugins.Plugin()
http_client = httpx.AsyncClient()

@plugin.slash_command()
async def osaker(inter: disnake.CommandInteraction):
    pass

@osaker.sub_command(description="Get a random osaker clip")
async def random(inter: disnake.CommandInteraction):
    await inter.response.defer()

    async with http_client as client:
        request = await client.get(f"{SATA_ANDAGI}/random")
        data = request.json()

    await inter.followup.send(f"{data['url']}")

@osaker.sub_command(description="Search for a random osaker clip")
async def search(
    inter: disnake.CommandInteraction,
    query: str     
):
    await inter.response.defer()

    async with http_client as client:
        request = await client.get(f"{SATA_ANDAGI}/search?query={query}")
        data = request.json()

        if data == []:
            embed = disnake.Embed(
                title = "OsakerNotFound", 
                description = "No osaker found based on your query 😔",
                color=0xDC143C
            )

            await inter.followup.send(embed=embed)
            return

        metadata = data[0]

    await inter.followup.send(metadata["url"])

@search.autocomplete("query")
async def query_autocomp(inter: disnake.ApplicationCommandInteraction, query: str):
    comps = []

    async with http_client as client:
        request = await client.get(f"{SATA_ANDAGI}/search?query={query}")

    for item in request.json():
        comps.append(item["title"])

    return comps

setup, teardown = plugin.create_extension_handlers()