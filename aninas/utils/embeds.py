from disnake import Embed
from ..constant import Emojis, Colours

import re

def error_embed(title: str, description: str) -> Embed:
    embed = Embed(
        title = f"{Emojis.error} {title}",
        description = description,
        color = Colours.error
    )

    return embed

def line_fix(string: str) -> str:
    return "".join(
        [re.sub(' +', ' ', line)[1 if string[0] == "\n" else 0:] + "\n" for line in string.splitlines()]
    )