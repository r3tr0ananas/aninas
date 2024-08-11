import asyncio
import disnake
from disnake.ext import commands
from aninas.constant import BOT_TOKEN

class MyBot(commands.InteractionBot):
    def __init__(self):
        intents = disnake.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"logged in as {str(self.user)}")

async def main():
    client = MyBot()
    client.load_extensions("aninas/plugins")
    await client.start(BOT_TOKEN)

asyncio.run(main())
