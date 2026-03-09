import requests
# from prefect import task
from prefect.logging import get_run_logger

def log_function_call(prefix: str = ""):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_run_logger()
            logger.info(f"[BEGIN]: {prefix}{func.__name__}")
            result = func(*args, **kwargs)
            logger.info(f"[END]: {prefix}{func.__name__}")
            return result
        return wrapper
    return decorator

# @task
def send_get_request(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f"Status: {response.status_code}, Message: {response.text}")
    data = response.json()
    return data

# @task
def extract_player_match_data(match_data, game_name, tagline):
    game_info = match_data['info']
    players_game_info = game_info['participants']
    player_match_data = filter(lambda x: x['riotIdGameName'] == game_name and x['riotIdTagline'] == tagline, players_game_info)
    return next(player_match_data)