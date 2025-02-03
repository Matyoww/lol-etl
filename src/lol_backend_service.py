import requests
from src.constants import Clusters

def send_get_request(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f"Status: {response.status_code}, Message: {response.text['status']['message']}")
    data = response.json()
    return data

class RiotAPI:
    def __init__(self, api_key):
        self.api_key = api_key


    def _url_builder(self, cluster, endpoint):
        url = endpoint
        if cluster == "ASIA":
            url = f"{Clusters.ASIA.value}{url}"
        elif cluster == "SEA":
            url = f"{Clusters.SEA.value}{url}"
        elif cluster == "PH2":
            url = f"{Clusters.PH2.value}{url}"
        url += f"&api_key={self.api_key}"
        return url

    
    def get_puuid_by_riot_id(self, game_name, tagline):
        endpoint = f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tagline}?"
        url = self._url_builder("ASIA", endpoint)
        data = send_get_request(url)
        return data['puuid']
    

    def get_riot_id_by_puuid(self, puuid):
        endpoint = f"/riot/account/v1/accounts/by-puuid/{puuid}?"
        url = self._url_builder("ASIA", endpoint)
        data = send_get_request(url)
        return {'game_name': data['gameName'], 'tagline': data['tagLine']}

    
    def get_free_champ_rotation(self, cluster):
        endpoint = "/lol/platform/v3/champion-rotations?"
        url = self._url_builder(cluster, endpoint)
        data = send_get_request(url)
        return data['freeChampionIds']
    

    def get_match_list(self, cluster, puuid, start = 0, count = 20):
        endpoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
        url = self._url_builder(cluster, endpoint)
        data = send_get_request(url)
        return data


    def get_match_data(self, cluster, match_id):
        endpoint = f"/lol/match/v5/matches/{match_id}?"
        url = self._url_builder(cluster, endpoint)
        data = send_get_request(url)
        return data