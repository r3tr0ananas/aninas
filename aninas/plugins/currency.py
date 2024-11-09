from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

import disnake
import disnake_plugins

from disnake.ext import tasks
from disnake.ext import commands

from currency_converter import CurrencyConverter, ECB_URL
from datetime import datetime

from ..utils.embed import line_fix

plugin = disnake_plugins.Plugin()

@plugin.register_loop()
@tasks.loop(hours=24)
async def update_c():
    global c
    c = CurrencyConverter(ECB_URL)

@plugin.slash_command(description="Convert currency from one currency to another. Exchange rates provided by the ECB.")
@commands.cooldown(1, 3, commands.BucketType.member)
async def convert(
    inter: disnake.CommandInteraction,
    amount: float = commands.Param(description="The quantity of the source currency."),
    source: str = commands.Param(description="The currency you're converting from."),
    target: str = commands.Param("USD", description="The currency you're converting to. Defaults to USD."),
    date: str = commands.Param(None, description="Optional date to fetch historical exchange rates. E.G: 2014-2-24")
):
    if date is not None:
        date = datetime.strptime(date, "%Y-%m-%d")

    converted = c.convert(amount, source.upper(), target.upper(), date)

    embed = disnake.Embed(
        title = f"{source} to {target}",
        description = line_fix(f"""
            {amount} {source} are {round(converted)} {target} (rounded)

            To be exact: {converted} {target}
        """),
        colour=disnake.Colour.green(),
        timestamp=date if date else datetime.now()
    )

    await inter.send(embed=embed)

@convert.autocomplete("source")
async def source_autocomp(_, query: str):
    currencies = c.currencies

    return [currency for currency in currencies if query.upper() in currency][:10]

@convert.autocomplete("target")
async def target_autocomp(_, query: str):
    currencies = c.currencies

    return [currency for currency in currencies if query.upper() in currency][:10]

setup, teardown = plugin.create_extension_handlers()
