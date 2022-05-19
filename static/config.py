from os import getenv
import re

pattern_redis = re.compile(r"redis:\/\/:(?P<password>[a-z0-9]*?)@(?P<host>[a-z0-9\-\.]*?):(?P<port>[0-9]*$)")

BOT_TOKEN = getenv("BOT_TOKEN")
BOT_OWNER = int(getenv("BOT_OWNER"))
MODERATORS = list(map(int, getenv("MODERATORS").split()))
DATABASE_URL = getenv("DATABASE_URL").replace("postgres://", "postgresql://")
REDIS_URL = re.search(pattern_redis, getenv("REDIS_URL")).groupdict()
