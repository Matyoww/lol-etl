import enum

class Clusters(enum.Enum):
    ASIA = "https://asia.api.riotgames.com"
    SEA = "https://sea.api.riotgames.com"
    PH2 = "https://ph2.api.riotgames.com"

    def __getattribute__(self, name):
        return super().__getattribute__(name)