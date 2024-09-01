import io

import disnake
import httpx

from disnake.ext import plugins, commands
from PIL import Image

from ..utils.quote import make_it_quote

plugin = plugins.Plugin()

@plugin.message_command(name="Quote this message")
@commands.cooldown(1, 3, commands.BucketType.member)
async def quote(inter: disnake.ApplicationCommandInteraction, message: disnake.Message):
    if len(message.content) > 30:
        return await inter.response.send_message("Message is too long to quote", ephemeral=True)

    await inter.response.defer()

    author_image = io.BytesIO(
        httpx.get(message.author.avatar.url).content
    )

    author_image = Image.open(author_image)

    img_buf = io.BytesIO()

    make_it_quote(
        author_image, 
        message.content, 
        message.author.name
    ).save(img_buf, format="png")

    img_buf.seek(0)

    await inter.followup.send(
        f"[Jump to message]({message.jump_url})",
        file=disnake.File(img_buf, f"{message.id}.png")
    )

setup, teardown = plugin.create_extension_handlers()