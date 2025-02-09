import os

default_values = {
    'PERSONAL_GAME_NAME': 'Matyoww',
    'PERSONAL_TAGLINE': '3263'
}

def set_environment():
    for key in default_values.keys():
        if key not in os.environ:
            os.environ[key] = default_values[key]