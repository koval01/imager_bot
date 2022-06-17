from aiologger import Logger
from aiologger.formatters.base import Formatter
from logging import INFO, DEBUG
import logging

import sys

is_debug_run = True if "debug_run" in sys.argv else False
log_format = "%(name)s - %(levelname)s - %(message)s"

logging.basicConfig(
    format=log_format,
    level=DEBUG if is_debug_run else INFO)
logger = Logger.with_default_handlers(
    level="DEBUG" if is_debug_run else "INFO",
    formatter=Formatter(log_format))
