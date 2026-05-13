import os

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

default_values = {
    'DB_PATH': './projects/lol-etl/db/lol_db_dev.db',
    'SETUP_SQL': './projects/lol-etl/db/setup_pg.sql',
    'RESET_SQL': './projects/lol-etl/db/reset_pg.sql'
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

    logger.info("Setting default environment variables if not already set.")
    for key in default_values.keys():
        if key not in os.environ:
            os.environ[key] = default_values[key]
