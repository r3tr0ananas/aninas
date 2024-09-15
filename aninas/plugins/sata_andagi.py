from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

import disnake
import disnake_plugins
from disnake.ext import commands

from ..utils.sata_andagi import SataAndagi

plugin = disnake_plugins.Plugin()

@plugin.load_hook(post=True)
async def set_sata_andagi():
    global sata_andagi
    sata_andagi = SataAndagi(plugin.bot.redis)

@plugin.slash_command()
async def osaker(inter):
    pass

@osaker.sub_command(description="Get a random osaker clip")
@commands.cooldown(1, 3, commands.BucketType.user)
async def random(inter: disnake.CommandInteraction):
    await inter.response.defer()

    url = await sata_andagi.random()

    await inter.followup.send(url)

@osaker.sub_command(description="Search for a osaker clip")
@commands.cooldown(1, 3, commands.BucketType.user)
async def search(
    inter: disnake.CommandInteraction,
    query: str = commands.Param(description="Query")
):
    await inter.response.defer()

    url = await sata_andagi.get(query)

    await inter.followup.send(url)

@search.autocomplete("query")
async def query_autocomp(inter: disnake.ApplicationCommandInteraction, query: str):
    return await sata_andagi.auto_comp(query)

setup, teardown = plugin.create_extension_handlers()