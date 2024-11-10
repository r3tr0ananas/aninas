import asyncio

import disnake
import udatetime
from disnake.ext import commands

from . import __version__
from .constant import BOT_TOKEN, Colours
from .database import Redis
from .utils import embed


class Aninas(commands.InteractionBot):
    def __init__(self):
        intents = disnake.Intents.default()
        intents.message_content = True

        disnake.Embed.set_default_colour(Colours.cerise)

        self._redis = Redis()
        self._started = int(udatetime.now().timestamp())

        super().__init__(
            intents=intents,
            activity=disnake.Activity(name=f"v{__version__}", state="Haiiii :3"),
        )

    @property
    def redis(self) -> Redis:
        return self._redis

    @property
    def started(self) -> int:
        return self._started

    async def on_ready(self):
        print(f"Ready: {str(self.user)}")

    async def close(self):
        await super().close()

        await self._redis.close()

    async def on_slash_command_error(
        self, inter: disnake.CommandInteraction, error: commands.CommandInvokeError
    ):
        if inter.response.is_done():
            return await inter.followup.send(
                embed=embed.error("Something went wrong", error.original)
            )

        await inter.response.send_message(
            embed=embed.error("Something went wrong", error.original)
        )


async def main():
    client = Aninas()
    client.load_extensions("aninas/plugins")
    await client.start(BOT_TOKEN)


asyncio.run(main())
