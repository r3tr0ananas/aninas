from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

import disnake
from disnake.ext import plugins, commands

from ..utils import sata_andagi, embeds
from ..constant import Emojis

plugin = plugins.Plugin()

@plugin.slash_command()
async def osaker(inter: disnake.CommandInteraction):
    pass

@osaker.sub_command(description="Get a random osaker clip")
@commands.cooldown(1, 3, commands.BucketType.user)
async def random(inter: disnake.CommandInteraction):
    await inter.response.defer()

    data = await sata_andagi.get_random()

    if isinstance(data, str):
        embed = embeds.error_embed("Error: sata-andagi", data)

        await inter.followup.send(embed=embed)
        return

    await inter.followup.send(data.url)

@osaker.sub_command(description="Search for a random osaker clip")
@commands.cooldown(1, 3, commands.BucketType.user)
async def search(
    inter: disnake.CommandInteraction,
    query: str     
):
    await inter.response.defer()

    data = await sata_andagi.search(query)

    if isinstance(data, str):
        embed = embeds.error_embed("Error: sata-andagi", data)

        await inter.followup.send(embed=embed)
        return

    if data is None:
        embed = embeds.error_embed(                 
            title = "OsakerNotFound", 
            description = f"No osaker found based on your query {Emojis.pensive}",
        )

        await inter.followup.send(embed=embed)
        return

    await inter.followup.send(data.url)

@search.autocomplete("query")
async def query_autocomp(inter: disnake.ApplicationCommandInteraction, query: str):
    return await sata_andagi.autocomplete(query)

setup, teardown = plugin.create_extension_handlers()