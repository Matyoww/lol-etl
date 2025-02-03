
import os
import utils
import pandas as pd
from lol_backend_service import RiotAPI
from dotenv import load_dotenv

load_dotenv()

riot_api = RiotAPI(os.getenv("PERSONAL_API_KEY"))
game_name = os.getenv("PERSONAL_GAME_NAME")
tagline = str(os.getenv("PERSONAL_TAGLINE"))

player_puuid = riot_api.get_puuid_by_riot_id(game_name, tagline)
match_list = riot_api.get_match_list("SEA", player_puuid, count=90)

player_match_list = []
df_player_matches = pd.DataFrame()
if os.path.exists(f'./player_matches/{game_name}_{tagline}_matches.csv'):
    os.makedirs('./player_matches', exist_ok=True)
    df_player_matches = pd.read_csv(f'./player_matches/{game_name}_{tagline}_matches.csv')
else:
    for match_id in match_list:
        match_data = riot_api.get_match_data("SEA", match_id)
        match_game_mode = match_data['info']['gameMode']

        match_data = utils.extract_player_match_data(match_data, game_name, tagline)
        match_data = {x: match_data[x] for x in match_data if x not in ['challenges', 'missions', 'perks']}
        match_data = pd.Series(match_data)

        match_data['matchId'] = match_id
        match_data['gameMode'] = match_game_mode

        player_match_list.append(match_data)

    df_player_matches = pd.DataFrame(player_match_list)
    df_player_matches.to_csv(f'./player_matches/{game_name}_{tagline}_matches.csv', index=False)