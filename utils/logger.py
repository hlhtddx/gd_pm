import logging
import os
from logging import DEBUG, WARN

_debug = os.environ.get('DEBUG', default=False)
log_level = DEBUG if _debug else WARN


def init_logger(filename, level):
    logger = logging.getLogger("GD-PM")
    logger.setLevel(level=level)
    handler = logging.FileHandler(filename)
    handler.setLevel(level=DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = init_logger('data/gpm.log', log_level)
