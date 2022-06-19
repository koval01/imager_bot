import logging
import sys
from logging import INFO, DEBUG

is_debug_run = True if "debug_run" in sys.argv else False
log_format = "%(name)s - %(levelname)s - %(message)s"

logging.basicConfig(
    format=log_format,
    level=DEBUG if is_debug_run else INFO)
