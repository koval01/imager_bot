from os import getenv
import re

pattern_redis = re.compile(r"redis:\/\/:(?P<password>[A-z0-9]*?)@(?P<host>[a-z0-9\-\.]*?):(?P<port>[0-9]*$)")

BOT_TOKEN = getenv("BOT_TOKEN")
BOT_OWNER = int(getenv("BOT_OWNER"))

APP_DOMAIN = getenv("APP_DOMAIN")
ALT_APP_DOMAIN = getenv("ALT_APP_DOMAIN")
DATABASE_URL = getenv("DATABASE_URL").replace("postgres://", "postgresql+asyncpg://")

DONATE_LINK = getenv("DONATE_LINK")
MANAGER_ID = getenv("MANAGER_ID")

REDIS_URL = re.search(pattern_redis, getenv("REDIS_URL")).groupdict()
REDIS_STORAGE = bool(getenv("REDIS_STORAGE"))
DISLIKE_DISABLED = bool(getenv("DISLIKE_DISABLED"))

GA_ID = getenv("GA_ID")
GA_SECRET = getenv("GA_SECRET")
