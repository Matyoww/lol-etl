import os

default_values = {
    'PERSONAL_GAME_NAME': 'Matyoww',
    'PERSONAL_TAGLINE': '3263',
    'DB_PATH': './db/lol_db_dev.db',
    'SETUP_SQL': './db/setup_sqlite.sql'
}

def set_environment():
    env_file = './.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

    for key in default_values.keys():
        if key not in os.environ:
            os.environ[key] = default_values[key]