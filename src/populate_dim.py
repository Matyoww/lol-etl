import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import send_get_request
from src.set_environment import set_environment
from src.constants import ChampionAPI
from interface.database import SQLiteClient

def get_latest_version():
    return send_get_request(ChampionAPI.VERSIONS.value)[0]

def get_champion_data(version):
    return send_get_request(ChampionAPI.CHAMPION.value.format(version=version))['data']

class PopulateDim:
    def __init__(self, table_name, data = None):
        set_environment()
        self.db_path = os.getenv('DB_PATH')
        self.table_name = table_name
        self.data = data

    def populate(self, custom_json = None):
        db_client = SQLiteClient(self.db_path)
        try:
            db_client.open_connection()
            column_list = db_client.cursor.execute(f"PRAGMA table_info({self.table_name})").fetchall()
            column_names = [col[1] for col in column_list]

            sql_script = f"INSERT INTO {self.table_name} ({', '.join(column_names)}) VALUES "
            if custom_json:
                with open(custom_json, 'r') as file:
                    json_data = json.load(file)
                sql_script += ','.join([f'("{json_data[item]["id"]}", "{json_data[item]["name"]}")' for item in json_data])
            else:
                sql_script += self.data
            sql_script += " ON CONFLICT DO NOTHING;"

            db_client.execute_query(sql_script)
            print(f"{self.table_name} populated successfully.")
        except Exception as e:
            print(f"An error occurred while populating {self.table_name}: {e}")
        finally:
            db_client.close_connection()

if __name__ == "__main__":
    version = get_latest_version()
    champion_data = get_champion_data(version)
    champion_data = [f"""("{value['key']}", "{value['name']}")""" for value in champion_data.values()]
    champion_data = ','.join(champion_data)
    singleton = PopulateDim('dim_champions', champion_data)
    singleton.populate()

    singleton = PopulateDim('dim_roles')
    singleton.populate(custom_json='./static/roles.json')

    singleton = PopulateDim('dim_results')
    singleton.populate(custom_json='./static/result.json')
