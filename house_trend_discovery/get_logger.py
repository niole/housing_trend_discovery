import logging
import os

def get_logger(name):
    level = os.environ.get("LOG_LEVEL", "INFO")
    logging.basicConfig(level=level)
    return logging.getLogger(name)
