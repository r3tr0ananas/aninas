import asyncio
from disnake.ext import commands
from aninas.constant import BOT_TOKEN

class MyBot(commands.InteractionBot):
    def __init__(self):
        super().__init__(test_guilds=[863416692083916820])

    async def on_ready(self):
        print(f"logged in as {str(self.user)}")

async def main():
    client = MyBot()
    client.load_extensions("aninas/plugins")
    await client.start(BOT_TOKEN)

asyncio.run(main())