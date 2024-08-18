from ..constant import Colours, Emojis

import disnake

import re

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

def line_fix(string: str) -> str:
    return "".join(
        [re.sub(' +', ' ', line)[1 if string[0] == "\n" else 0:] + "\n" for line in string.splitlines()]
    )