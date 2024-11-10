import math
from collections.abc import Iterable
from typing import Generator

from PIL import Image, ImageDraw, ImageFont

from ..constant import QUOTE_FONT, THIS_IS_FONT, THIS_IS_TEMPLATE

BG_COLOR = (32, 32, 32, 255)
TARGET_HEIGHT = 128
TARGET_WIDTH = 600
START_X = 40
TEXT_COLOR = (255, 255, 255, 255)

# Thanks to [Tea](https://github.com/teaishealthy) for making the make_it_quote function :3


def interpolate(
    start_color: Iterable[int], end_color: Iterable[int], interval: int
) -> Generator[Generator[int, None, None], None, None]:
    color_change = [(t - f) / interval for f, t in zip(start_color, end_color)]
    for i in range(interval):
        yield (round(f + det * i) for f, det in zip(start_color, color_change))


def color_easing(t: float) -> float:
    # ease_in_out_cubic
    return -(math.cos(math.pi * t) - 1) / 2


def make_it_quote(profile_picture: Image.Image, text: str, author: str) -> Image.Image:
    # Add text to the image
    ratio = profile_picture.height / TARGET_HEIGHT
    profile_picture = profile_picture.resize(
        (int(profile_picture.width / ratio), TARGET_HEIGHT)
    )

    quote_image = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), color=BG_COLOR)

    quote_image.paste(profile_picture, (0, 0))

    gradient = Image.new("RGBA", quote_image.size, color=0)

    draw = ImageDraw.Draw(gradient)

    end_x = profile_picture.width

    for i, co in enumerate(interpolate([0, 0, 0, 0], BG_COLOR, end_x - START_X)):
        t = i / (end_x - START_X)
        co = [round(color_easing(t) * c) for c in co]
        draw.line(
            [(START_X + i, 0), (START_X + i, TARGET_HEIGHT)],
            fill=tuple(co),  # type: ignore
            width=1,
        )
    quote_image = Image.alpha_composite(quote_image, gradient)
    draw = ImageDraw.Draw(quote_image)

    font = ImageFont.truetype(QUOTE_FONT, 32)

    _, _, _, height = draw.textbbox((profile_picture.width, 0), text, font=font)
    x = profile_picture.width + 40
    center_y = TARGET_HEIGHT // 2 - height
    draw.text(  # type: ignore
        (x, center_y),
        text,
        font=font,
        fill=TEXT_COLOR,
    )
    font = ImageFont.truetype(QUOTE_FONT, 16)
    draw.text(  # type: ignore
        (x, center_y + height + 10),
        f"- {author}",
        font=font,
        fill=TEXT_COLOR,
    )

    return quote_image


def make_this_is(who: str, image: Image.Image) -> Image.Image:
    font = ImageFont.truetype(THIS_IS_FONT, size=128)

    image = image.resize((1280, 780))

    template = Image.open(THIS_IS_TEMPLATE)

    template.paste(image, (0, 500))

    draw = ImageDraw.Draw(template)
    _, _, width, _ = draw.textbbox((0, 0), who, font=font)

    draw.text(((template.width - width) / 2, 250), who, font=font, fill=(0, 0, 0, 0))

    return template
