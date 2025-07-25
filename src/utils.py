import requests
import json

def send_get_request(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f"Status: {response.status_code}, Message: {response.text}")
    data = response.json()
    return data

def extract_player_match_data(match_data, game_name, tagline):
    game_info = match_data['info']
    players_game_info = game_info['participants']
    player_match_data = filter(lambda x: x['riotIdGameName'] == game_name and x['riotIdTagline'] == tagline, players_game_info)
    return next(player_match_data)