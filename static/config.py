from os import getenv
import re

pattern_redis = re.compile(r"redis:\/\/:(?P<password>[a-z0-9]*?)@(?P<host>[a-z0-9\-\.]*?):(?P<port>[0-9]*$)")
pattern_postgres = re.compile(r"postgresql:\/\/(?P<user>[A-z0-9]*?):(?P<password>[A-z0-9]*?)@(?P<host>[A-z0-9\-\.]*?)"
                              r":(?P<port>[0-9]{4,5})\/(?P<database>[A-z0-9]*$)")

BOT_TOKEN = getenv("BOT_TOKEN")
BOT_OWNER = int(getenv("BOT_OWNER"))
APP_DOMAIN = getenv("APP_DOMAIN")
MODERATORS = list(map(int, getenv("MODERATORS").split()))
DATABASE_URL = getenv("DATABASE_URL").replace("postgres://", "postgresql://")
DATABASE_URL_ELS = re.search(pattern_postgres, DATABASE_URL).groupdict()
REDIS_URL = re.search(pattern_redis, getenv("REDIS_URL")).groupdict()
