from decouple import config

__all__ = (
    "AGAC_URL",
    "SATA_ANDAGI",
    "BOT_TOKEN"
)

AGAC_URL = config("AGAC_URL", default = "https://api.ananas.moe/agac/v1")
SATA_ANDAGI = config("SATA_ANDAGI", default = "https://sata-andagi.moe/api")
CODEBERG = config("CODEBERG", default = "https://codeberg.org/api/v1")
CODEBERG_KEY = config("CODEBERG_KEY", default = "")
BOT_TOKEN = config("BOT_TOKEN", cast = str)