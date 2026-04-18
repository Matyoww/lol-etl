import logging
import requests
from src.constants import Clusters
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

class RiotHandler(ABC):
    @abstractmethod
    def handle(self, *args, **kwargs):
        pass

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
        else:
            logger.error(f"Unsupported cluster: {cluster}")
            raise ValueError(f"Unsupported cluster: {cluster}")
        url += f"&api_key={self.api_key}"
        return url

    def send_get_request(self, url):
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(
                f"Status: {response.status_code}, Message: {data['status']['message']}"
            )
        return data


class GetPuuidByRiotId(RiotHandler):
    def handle(self, game_name, tagline):
        endpoint = f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tagline}?"
        url = self._url_builder("ASIA", endpoint)
        data = self.send_get_request(url)
        return data['puuid']


class GetRiotIdByPuuid(RiotHandler):
    def handle(self, puuid):
        endpoint = f"/riot/account/v1/accounts/by-puuid/{puuid}?"
        url = self._url_builder("ASIA", endpoint)
        data = self.send_get_request(url)
        return {'game_name': data['gameName'], 'tagline': data['tagLine']}


class GetFreeChampRotation(RiotHandler):
    def handle(self, cluster):
        endpoint = "/lol/platform/v3/champion-rotations?"
        url = self._url_builder(cluster, endpoint)
        data = self.send_get_request(url)
        return data['freeChampionIds']


class GetMatchList(RiotHandler):
    def handle(self, cluster, puuid, start=0, count=20):
        endpoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
        url = self._url_builder(cluster, endpoint)
        data = self.send_get_request(url)
        return data


class GetMatchData(RiotHandler):
    def handle(self, cluster, match_id):
        endpoint = f"/lol/match/v5/matches/{match_id}?"
        url = self._url_builder(cluster, endpoint)
        data = self.send_get_request(url)
        return data


class APIService(ABC):
    @abstractmethod
    def dispatch(self, handler_name, *args, **kwargs):
        pass


class RiotAPI(APIService):
    def __init__(self, api_key):
        self.handlers = {
            "GetPuuidByRiotId": GetPuuidByRiotId(api_key),
            "GetRiotIdByPuuid": GetRiotIdByPuuid(api_key),
            "GetFreeChampRotation": GetFreeChampRotation(api_key),
            "GetMatchList": GetMatchList(api_key),
            "GetMatchData": GetMatchData(api_key)
        }

    def dispatch(self, handler_name, *args, **kwargs):
        if handler_name in self.handlers:
            return self.handlers[handler_name].handle(*args, **kwargs)
        else:
            raise ValueError(f"Handler {handler_name} not found.")
