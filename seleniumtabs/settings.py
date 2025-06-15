# https://github.com/pjialin/django-environ

import logging
import logging.config
import os
from pathlib import Path

import environ
import yaml

BASE_DIR = Path(__file__).parent

LOG_CONF_FILE = "log_config/log_config.yaml"
ENV_FILE = "../.env"

env = environ.Env()

env_file = BASE_DIR / Path(ENV_FILE)
env.read_env(env_file=env_file)


def setup_logging(path: str | Path = BASE_DIR / LOG_CONF_FILE, default_level: int = logging.INFO) -> None:
    """Setup logging configuration if not already configured.

    Args:
        path: Path to the logging configuration file
        default_level: Default logging level
    """
    # Check if logging is already configured
    if logging.getLogger().handlers:
        return

    if os.path.exists(path):
        with open(path) as f:
            config = yaml.safe_load(f.read())

            # Create logs directory if it doesn't exist
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)

            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        logging.warning(f"Logging config file not found at {path}. Using basic config.")


setup_logging()
