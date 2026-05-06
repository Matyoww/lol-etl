import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import send_get_request
from src.set_environment import set_environment
from src.constants import ChampionAPI
from interface.database import SQLiteClient, PostgreSQLClient, DatabaseClient

def get_latest_version():
    return send_get_request(ChampionAPI.VERSIONS.value)[0]

def get_champion_data(version):
    return send_get_request(ChampionAPI.CHAMPION.value.format(version=version))['data']

class PopulateDim:
    def __init__(self, table_name, data = None):
        set_environment()
        self.db_path = os.getenv('DB_PATH')
        self.table_name = table_name
        self.data = data  # list of tuples, e.g. [('1', 'Aatrox'), ('2', "Kai'Sa")]

    def populate(self, custom_json = None):
        db_client = PostgreSQLClient()
        try:
            db_client.open_connection()
            column_list = db_client.fetch_all(
                "SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position",
                (self.table_name,)
            )
            column_names = [col[0] for col in column_list]

            if custom_json:
                with open(custom_json, 'r') as file:
                    json_data = json.load(file)
                rows = [(item['id'], item['name']) for item in json_data.values()]
            else:
                rows = self.data

            placeholders = ', '.join(['%s'] * len(column_names))
            sql_script = f"INSERT INTO {self.table_name} ({', '.join(column_names)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

            for row in rows:
                db_client.execute_query(sql_script, row)

            print(f"{self.table_name} populated successfully.")
        except Exception as e:
            print(f"An error occurred while populating {self.table_name}: {e}")
        finally:
            db_client.close_connection()


def populate_dimensions():
    version = get_latest_version()
    champion_data = get_champion_data(version)
    champion_data = [(value['key'], value['name']) for value in champion_data.values()]
    singleton = PopulateDim('dim_champions', champion_data)
    singleton.populate()

    root_dir = os.path.dirname(os.path.abspath(__file__))
    singleton = PopulateDim('dim_roles')
    singleton.populate(custom_json=os.path.join(root_dir, '..', 'static', 'roles.json'))

    singleton = PopulateDim('dim_results')
    singleton.populate(custom_json=os.path.join(root_dir, '..', 'static', 'result.json'))

if __name__ == "__main__":
    populate_dimensions()
