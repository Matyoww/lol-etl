
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
except Exception as e:
    if "UNIQUE constraint failed" in str(e):
        print(f"Player already exists: {game_name}#{tagline}")
    else:
        print(f"Error occurred 'player puuid': {e}")
finally:
    db_client.close_connection()

# Get match list for the player
match_list = riot_api.dispatch("GetMatchList", "SEA", player_puuid, count=20)

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
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            print(f"Match already exists: {match_id}")
        else:
            print(f"Error occurred 'match': {e}")
    finally:
        db_client.close_connection()

    p_match_data = utils.extract_player_match_data(match_data, game_name, tagline)

    p_data = {
        'PUUID': player_puuid,
        'MatchID': match_id,
        'ChampionID': p_match_data['championId'],
        'Kills': p_match_data['kills'],
        'Deaths': p_match_data['deaths'],
        'Assists': p_match_data['assists'],
        'GoldEarned': p_match_data['goldEarned'],
        'DamageDealt': p_match_data['totalDamageDealt'],
        'DamageTaken': p_match_data['totalDamageTaken'],
        'VisionScore': p_match_data['visionScore'],
        'MinionsKilled': p_match_data['totalMinionsKilled']
    }

    p_data['RoleID'] = db_client.map_value_to_id(
        table='dim_roles',
        pk_column='RoleID',
        val_column='RoleName',
        value=p_match_data['role']
    )

    p_data['ChampionID'] = db_client.map_value_to_id(
        table='dim_champions',
        pk_column='ChampionID',
        val_column='ChampionName',
        value=p_match_data['championName']
    )

    df_player_matches = pd.concat([df_player_matches, pd.DataFrame([p_data])], ignore_index=True)

    sql = """
        INSERT INTO fact_player_performances (
            PUUID,
            MatchID,
            RoleID,
            ChampionID,
            Kills,
            Deaths,
            Assists,
            GoldEarned,
            DamageDealt,
            DamageTaken,
            VisionScore,
            MinionsKilled
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    try:
        db_client.open_connection()
        db_client.execute_query(sql, (
            p_data['PUUID'],
            p_data['MatchID'],
            p_data['RoleID'],
            p_data['ChampionID'],
            p_data['Kills'],
            p_data['Deaths'],
            p_data['Assists'],
            p_data['GoldEarned'],
            p_data['DamageDealt'],
            p_data['DamageTaken'],
            p_data['VisionScore'],
            p_data['MinionsKilled']
        ))
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            print(f"Player performance already exists: {p_data['PUUID']} - {p_data['MatchID']}")
        else:
            print(f"Error occurred 'player performance': {e}")
    finally:
        db_client.close_connection()
