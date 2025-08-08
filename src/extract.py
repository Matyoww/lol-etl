
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import utils
import pandas as pd
from interface.database import SQLiteClient
from lol_api_service import RiotAPI
from set_environment import set_environment

set_environment()

riot_api = RiotAPI(os.getenv("PERSONAL_API_KEY"))
game_name = os.getenv("PERSONAL_GAME_NAME")
tagline = str(os.getenv("PERSONAL_TAGLINE"))

db_client = SQLiteClient(os.getenv("DB_PATH"))

# Get player PUUID from Riot ID
player_puuid = riot_api.dispatch("GetPuuidByRiotId", game_name, tagline)
try:
    sql = """
        INSERT INTO dim_players (PUUID, RiotIDGameName, RiotTagLine)
        VALUES (?, ?, ?)
    """
    db_client.open_connection()
    db_client.execute_query(sql, (player_puuid, game_name, tagline))
    db_client.close_connection()
except Exception as e:
    if "UNIQUE constraint failed" in str(e):
        print(f"Player already exists: {game_name}#{tagline}")
    else:
        print(f"Error occurred: {e}")

# Get match list for the player
match_list = riot_api.dispatch("GetMatchList", "SEA", player_puuid, count=10)

player_match_list = []
df_player_matches = pd.DataFrame()

for match_id in match_list:
    match_data = riot_api.dispatch("GetMatchData", "SEA", match_id)
    match_game_mode = match_data['info']['gameMode']

    try:
        sql = """
            INSERT INTO dim_matches (MatchID, GameMode)
            VALUES (?, ?)
        """
        db_client.open_connection()
        db_client.execute_query(sql, (match_id, match_game_mode))
        db_client.close_connection()
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            print(f"Match already exists: {match_id}")
        else:
            print(f"Error occurred: {e}")

    match_data = utils.extract_player_match_data(match_data, game_name, tagline)
