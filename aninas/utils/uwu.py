import random

UWU = [
    ">~<",
    ">w<",
    "^w^",
    "UwU",
    "OwO",
    ":3",
    ";3",
    ">///<",
    ":p",
    ";p",
    "nya",
    "rawr x3",
    "o.O",
    "-.-",
    "(⑅˘꒳˘)",
    "(ꈍᴗꈍ)",
    "(˘ω˘)",
    "(U ᵕ U❁)",
    "σωσ",
    "òωó",
    "(///ˬ///✿)",
    "( ͡o ω ͡o )",
    "^•ﻌ•^",
    "/(^•ω•^)",
    "nyaa~~",
    "mya",
    "rawr",
]

LETTER_REPLACEMENTS = {"r": "w", "l": "w", "R": "W", "L": "W"}

ENDING_REPLACEMENTS = {
    "!": lambda: random.choice(UWU),
    "?": lambda: random.choice(UWU),
    ".": lambda: random.choice(UWU),
    ",": lambda: random.choice(UWU),
}

WORD_REPLACEMENTS = {
    "no": "nyo",
    "na": "nya",
    "mo": "mowo",
    "ne": "nye",
    "ni": "nyi",
    "nu": "nyu",
    "ho": "hwo",
    "small": "smol",
    "cute": "kawaii~",
    "fluff": "floof",
    "love": "luv",
    "stupid": "baka",
    "what": "nani",
    "meow": "nya~",
}


def uwuify(text: str) -> str:
    for replacement in WORD_REPLACEMENTS:
        text = text.replace(replacement, WORD_REPLACEMENTS[replacement])

    for replacement in LETTER_REPLACEMENTS:
        new_text = []
        words = text.split()

        for word in words:
            if word not in WORD_REPLACEMENTS.values():
                word = word.replace(replacement, LETTER_REPLACEMENTS[replacement])

            new_text.append(word)

        text = " ".join(new_text)

    stuttered = []
    words = text.split()

    for word in words:
        if random.random() < 0.2:
            stuttered.append(f"{word[0]}-{word}")
        else:
            stuttered.append(word)

    text = " ".join(stuttered)

    for replacement in ENDING_REPLACEMENTS:
        new_text = []

        for word in text.split():
            if len(word) > 1 and word[-1] == replacement and word[-2].isascii():
                uwu = ENDING_REPLACEMENTS[replacement]()
                word = f"{word} {uwu}"

            new_text.append(word)

        text = " ".join(new_text)

    if text.startswith("`"):
        text = "\u200b" + text
    text = text.replace("`", "`\u200b")

    return text
