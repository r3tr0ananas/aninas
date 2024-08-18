from ..constant import Colours, Emojis

import disnake

def error(
    title: str, 
    description: str,
    colour: Colours = Colours.error,
    error_emoji: Emojis = Emojis.error
) -> disnake.Embed:
    return disnake.Embed(
        title = f"{error_emoji} {title}",
        description = description,
        colour = colour
    )