import re

from decouple import config

class Emojis:
    pulls_open = "<:pr_open:1272273151182503966>"
    pulls_merged = "<:pr_merged:1272273030013390888>"
    pulls_draft = "<:pr_draft:1276507629992148992>"
    pulls_closed = "<:pr_closed:1272273006479147152>"
    issues_open = "<:issues_open:1272272998820483144>"
    issues_closed = "<:issues_closed:1272272990754836641>"

    repo = "<:repo:1273313627415380109>"
    follow = "<:follow:1273331809874214972>"
    fork = "<:fork:1273332307692093470>"
    link = "<:link:1273332935554236520>"

    information = ":information_source:"
    tv = "📺"

    error = "<a:error:1272561118052614307>"
    loading_cat = "<a:loading_cat:1273006525845082275>"

    eye = "👁️"
    star = "⭐"
    fork_footer = "⑂"
    pensive = "😔"
    notepad = "🗒️"
    zap = "⚡"
    package = "📦"

class Colours:
    error = 0xFF0000

    pulls_open = 0x87ab63
    pulls_merged = 0xb259d0
    pulls_draft = 0xd2e0f0
    pulls_closed = 0xcc4848
    issues_open = 0x87ab63
    issues_closed = 0xcc4848

    cerise = 0xDE3163

THIS_IS_TEMPLATE = config("THIS_IS_TEMPLATE", default = "resources/this_is.jpg")
THIS_IS_FONT = config("FONT", default = "resources/poppins.ttf")
QUOTE_FONT = config("THIS_IS_TEMPLATE", default = "resources/ubuntu.ttf")
REDIS = config("REDIS", default = "redis://localhost:6379")
LIMIT_CHAR = config("LIMIT_CHAR", default = 240)
CODEBERG_KEY = config("CODEBERG_KEY", cast = str)
TMDB_KEY = config("TMDB_KEY", cast = str)
BOT_TOKEN = config("BOT_TOKEN", cast = str)

CODEBERG_ISSUE_LINK_REGEX = re.compile(
    r"https?:\/\/codeberg.org\/(?P<repo>[a-zA-Z0-9-]+\/[\w.-]+)\/"
    r"(?P<type>issues|pulls)\/(?P<number>[0-9]+)[^\s]*"
)

CODEBERG_RE = re.compile(
    r"https?:\/\/codeberg.org\/(?P<repo>[a-zA-Z0-9-]+\/[\w.-]+)\/src\/(?P<path>[^#>]+)(\?[^#>]+)?"
    r"(?:#L(?P<start_line>\d+)(?:-L(?P<end_line>\d+))?)?"
)

CODEBERG_COMMENT_LINK_REGEX = re.compile(
    r"https?:\/\/codeberg.org\/(?P<repo>[a-zA-Z0-9-]+\/[\w.-]+)\/"
    r"(?P<type>issues|pulls)\/(?P<number>[0-9]+)\/?#issuecomment-(?P<comment_id>[0-9]+)[^\s]*"
)

AUTOMATIC_REGEX = re.compile(
    r"(?P<repo>[a-zA-Z0-9-]+\/[\w.-]+)#(?P<number>[0-9]+)"
)

LINK_REGEX = re.compile(
    r'\bhttps?:\/\/[^\s\]\)<>"]+|[a-zA-Z0-9-]+\/[\w.-]+#[0-9]+'
)