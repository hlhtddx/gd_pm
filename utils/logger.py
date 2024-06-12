from logging import Logger, DEBUG, WARN
import os

_debug = os.environ.get('DEBUG', default=False)
debug_level = DEBUG if _debug else WARN

logger = Logger('FeishuDA', level=debug_level)
