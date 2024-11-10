from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

import disnake
import disnake_plugins

from disnake.ext import commands

from ..utils.arch import Arch

plugin = disnake_plugins.Plugin()


@plugin.load_hook()
async def set_codeberg():
    global repo
    repo = Arch(plugin.bot.redis)


@plugin.slash_command(description="Get data from the AUR")
@commands.cooldown(1, 3, commands.BucketType.member)
async def aur(
    inter: disnake.CommandInteraction,
    package: str = commands.Param(
        description="The package name you're trying to search."
    ),
):
    aur_package = await repo.aur(package)

    embed = disnake.Embed(
        title=f"{package} {aur_package.version}",
        description=aur_package.description,
        timestamp=aur_package.last_update,
    )

    embed.set_thumbnail("https://cdn.ananas.moe/arch.png")

    embed.url = f"https://aur.archlinux.org/packages/{package}"

    embed.add_field("Out of date", aur_package.out_of_date)

    embed.set_footer(text="Last updated")

    await inter.send(embed=embed)


@plugin.slash_command(description="Get data from the arch repo")
@commands.cooldown(1, 3, commands.BucketType.member)
async def pacman(
    inter: disnake.CommandInteraction,
    package: str = commands.Param(
        description="The package name you're trying to search."
    ),
):
    pac_package = await repo.pacman(package)

    embed = disnake.Embed(
        title=f"{package} {pac_package.version} ({pac_package.repo}, {pac_package.arch})",
        description=pac_package.description,
        timestamp=pac_package.last_update,
    )

    embed.set_thumbnail("https://cdn.ananas.moe/arch.png")

    embed.url = f"https://archlinux.org/packages/{package}"

    embed.add_field("Out of date", pac_package.out_of_date)

    embed.set_footer(text="Last updated")

    await inter.send(embed=embed)


@aur.autocomplete("package")
async def aur_autocomp(_, query: str):
    return await repo.aur_search(query)


@pacman.autocomplete("package")
async def pacman_autocomp(_, query: str):
    return await repo.pacman_search(query)


setup, teardown = plugin.create_extension_handlers()
