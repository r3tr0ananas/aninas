from disnake import Embed
from ..constant import Emojis, Colours

def error_embed(title: str, description: str) -> Embed:
    embed = Embed(
        title = f"{Emojis.error} {title}",
        description = description,
        color = Colours.error
    )

    return embed