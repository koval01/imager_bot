from os import getenv

BOT_TOKEN = getenv("BOT_TOKEN")
BOT_OWNER = getenv("BOT_OWNER")
MODERATORS = [int(i) for i in getenv("MODERATORS").split()]
DATABASE_URL = getenv("DATABASE_URL")
