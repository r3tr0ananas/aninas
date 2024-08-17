import asyncio
import disnake
from disnake.ext import commands    

from aninas.utils.redis import Redis
from aninas.constant import BOT_TOKEN

class MyBot(commands.InteractionBot):
    def __init__(self):
        intents = disnake.Intents.default()
        intents.message_content = True

        self.redis = Redis()

        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"logged in as {str(self.user)}")

async def main():
    client = MyBot()
    client.load_extensions("aninas/plugins")
    try:
        await client.start(BOT_TOKEN)
    except (KeyboardInterrupt, asyncio.CancelledError):
        await client.redis.close()

asyncio.run(main())
