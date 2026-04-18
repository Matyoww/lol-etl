import os

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

default_values = {
    'PERSONAL_GAME_NAME': 'Matyoww',
    'PERSONAL_TAGLINE': '3263',
    'DB_PATH': './db/lol_db_dev.db',
    'SETUP_SQL': './db/setup_pg.sql'
}

def set_environment():
    logger.info("Setting environment variables from .env file if it exists.")

    env_file = './.env'
    if os.path.exists(env_file):
        logger.info(f".env file found at {env_file}, loading variables.")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and line != '':
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    else:
        logger.warning(f"No .env file found at {env_file}, relying on existing environment variables.")

    logger.info("Setting default environment variables if not already set.")
    for key in default_values.keys():
        if key not in os.environ:
            os.environ[key] = default_values[key]
