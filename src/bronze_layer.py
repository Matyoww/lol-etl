import os
import sys
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.lol_api_service import RiotAPI
from src.set_environment import set_environment
from src.bigquery.insert import insert_match_to_bronze

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%    (levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)


def get_match_data(match_id):
    riot_api = RiotAPI(os.getenv("PERSONAL_API_KEY"))
    match_data = riot_api.dispatch("GetMatchData", "SEA", match_id)
    return match_data


def fetch_match_ids(count=20):
    riot_api = RiotAPI(os.getenv("PERSONAL_API_KEY"))
    game_name = os.getenv("PERSONAL_GAME_NAME")
    tagline = str(os.getenv("PERSONAL_TAGLINE"))

    player_puuid = riot_api.dispatch("GetPuuidByRiotId", game_name, tagline)
    match_list = riot_api.dispatch("GetMatchList", "SEA", player_puuid, count=count)

    return match_list


def main():
    set_environment()

    match_list = fetch_match_ids(count=20)

    for match_id in match_list:
        match_raw_data = get_match_data(match_id)
        insert_match_to_bronze(match_raw_data)


if __name__ == "__main__":
    main()