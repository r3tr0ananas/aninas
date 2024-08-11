import disnake
from disnake.ext import plugins, commands
import httpx

from ..constant import SATA_ANDAGI
from ..types.sata_andagi import SataAndagi

plugin = plugins.Plugin()
client = httpx.AsyncClient()

@plugin.slash_command()
async def osaker(inter: disnake.CommandInteraction):
    pass

@osaker.sub_command(description="Get a random osaker clip")
@commands.cooldown(1, 3, commands.BucketType.user)
async def random(inter: disnake.CommandInteraction):
    await inter.response.defer()

    request = await client.get(f"{SATA_ANDAGI}/random")
    data = SataAndagi(request.json())

    await inter.followup.send(data.url)

@osaker.sub_command(description="Search for a random osaker clip")
@commands.cooldown(1, 3, commands.BucketType.user)
async def search(
    inter: disnake.CommandInteraction,
    query: str     
):
    await inter.response.defer()

    request = await client.get(f"{SATA_ANDAGI}/search?query={query}")
    data = request.json()

    if data == []:
        embed = disnake.Embed(
            title = "OsakerNotFound", 
            description = "No osaker found based on your query 😔",
            color=0xFF0000
        )

        await inter.followup.send(embed=embed)
        return

    metadata = SataAndagi(data[0])

    await inter.followup.send(metadata.url)

@search.autocomplete("query")
async def query_autocomp(inter: disnake.ApplicationCommandInteraction, query: str):
    comps = []

    request = await client.get(f"{SATA_ANDAGI}/search?query={query}")

    for item in request.json():
        comps.append(item["title"]) 

    return comps

setup, teardown = plugin.create_extension_handlers()
