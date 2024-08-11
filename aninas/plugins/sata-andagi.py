import disnake
from disnake.ext import plugins, commands

from ..utils import sata_andagi

plugin = plugins.Plugin()

@plugin.slash_command()
async def osaker(inter: disnake.CommandInteraction):
    pass

@osaker.sub_command(description="Get a random osaker clip")
@commands.cooldown(1, 3, commands.BucketType.user)
async def random(inter: disnake.CommandInteraction):
    await inter.response.defer()

    data = await sata_andagi.get_random()

    await inter.followup.send(data.url)

@osaker.sub_command(description="Search for a random osaker clip")
@commands.cooldown(1, 3, commands.BucketType.user)
async def search(
    inter: disnake.CommandInteraction,
    query: str     
):
    await inter.response.defer()

    metadata = await sata_andagi.search(query)

    if metadata is None:
        embed = disnake.Embed(
            title = "OsakerNotFound", 
            description = "No osaker found based on your query 😔",
            color=0xFF0000
        )

        await inter.followup.send(embed=embed)
        return

    await inter.followup.send(metadata.url)

@search.autocomplete("query")
async def query_autocomp(inter: disnake.ApplicationCommandInteraction, query: str):
    return await sata_andagi.autocomplete(query)

setup, teardown = plugin.create_extension_handlers()
