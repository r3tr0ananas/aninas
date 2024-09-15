from PIL import Image, ImageDraw, ImageFont

from ..constant import THIS_IS_TEMPLATE, FONT

def make_this_is(who: str, image: Image.Image) -> Image.Image:
    font = ImageFont.truetype(FONT, size=128)

    image = image.resize(
        (1280, 780)
    )

    template = Image.open(THIS_IS_TEMPLATE)

    template.paste(image, (0, 500))
    
    draw = ImageDraw.Draw(template)
    _, _, width, _ = draw.textbbox((0, 0), who, font=font)

    draw.text(
        ((template.width - width) / 2, 250),
        who,
        font=font,
        fill=(0, 0, 0, 0)
    )

    return template