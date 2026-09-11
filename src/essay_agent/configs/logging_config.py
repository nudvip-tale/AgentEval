import logging
from logging.config import dictConfig
import os

import yaml


def init_logging():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env = os.getenv('ENV_FOR_DYNACONF', default=None)
    if not env:
        raise ValueError("Set appropriate env to load the logger")
    with open(f"{path}/logger.yaml", 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config[env])
        return config[env]