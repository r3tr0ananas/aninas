import io

import disnake
import disnake_plugins
import httpx

from disnake.ext import commands
from PIL import Image

from ..utils.images import make_it_quote, make_this_is

plugin = disnake_plugins.Plugin()

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

@plugin.slash_command(description="Make a \"This is\" meme")
@commands.cooldown(1, 10, commands.BucketType.member)
async def this_is(
    inter: disnake.ApplicationCommandInteraction,
    who: str = commands.Param(description="Who is it?", max_length=20),
    attachment: disnake.Attachment = commands.Param(description="Attach an image"),
):
    await inter.response.defer()
    
    image_data = io.BytesIO(
        await attachment.read()
    )

    image = Image.open(
        image_data
    )

    img_buf = io.BytesIO()

    make_this_is(
        who,
        image
    ).save(img_buf, format="png")

    img_buf.seek(0)

    await inter.followup.send(
        file=disnake.File(img_buf, f"{who}.png")
    )

setup, teardown = plugin.create_extension_handlers()