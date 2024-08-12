from decouple import config

class Emojis:
    error = "<a:error:1272561118052614307>"

    pulls_open = "<:pr_open:1272273151182503966>"
    pulls_merged = "<:pr_merged:1272273030013390888>"
    pulls_draft = "<:pr_draft:1272535045172625439>"
    pulls_closed = "<:pr_closed:1272273006479147152>"
    issues_open = "<:issues_open:1272272998820483144>"
    issues_closed = "<:issues_closed:1272272990754836641>"

    star = "⭐"
    fork = "⑂"
    pensive = "😔"
    notepad = "🗒️"
    zap = "⚡"
    package = "📦"

class Colours:
    error = 0xFF0000

    pulls_open = 0x87ab63
    pulls_merged = 0xb259d0
    pulls_draft = 0x33393e
    pulls_closed = 0xcc4848
    issues_open = 0x87ab63
    issues_closed = 0xcc4848

    cerise = 0xDE3163


AGAC_URL = config("AGAC_URL", default = "https://api.ananas.moe/agac/v1")
SATA_ANDAGI = config("SATA_ANDAGI", default = "https://sata-andagi.moe/api")
CODEBERG = config("CODEBERG", default = "https://codeberg.org/api/v1")
CODEBERG_KEY = config("CODEBERG_KEY", default = "")
BOT_TOKEN = config("BOT_TOKEN", cast = str)
