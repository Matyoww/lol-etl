import os
import json
from lol_backend_service import RiotAPI

def get_champion_mapping(champ_id_list):
    with open('./metadata/champion.json') as f:
        champ_data = json.load(f)

    champ_mapping = {int(champ_data['data'][key]['key']):champ_data['data'][key]['name'] for key in champ_data['data'].keys()}
    champ_list = {champ_mapping[key] for key in champ_id_list}
    return champ_list

def extract_player_match_data(match_data, game_name, tagline):
    game_info = match_data['info']
    players_game_info = game_info['participants']
    player_match_data = filter(lambda x: x['riotIdGameName'] == game_name and x['riotIdTagline'] == tagline, players_game_info)
    return next(player_match_data)