import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import Clusters
from utils import send_get_request
from src.set_environment import set_environment
from interface.database import SQLiteClient

class SetupDatabase:
    def __init__(self, db_path: str, sql_script: str):
        self.db_client = SQLiteClient(db_path)
        self.sql_script = sql_script
        
    def setup(self):
        try:
            self.db_client.open_connection()

            with open(self.sql_script, 'r') as file:
                sql_script_content = file.read()

            self.db_client.execute_script(sql_script_content)
            print("Database setup completed successfully.")
        except Exception as e:
            print(f"An error occurred during database setup: {e}")
        finally:
            self.db_client.close_connection()


if __name__ == "__main__":
    set_environment()

    db_path = os.getenv('DB_PATH')
    sql_script = os.getenv('SETUP_SQL')
    
    if not os.path.exists(sql_script):
        print(f"SQL script '{sql_script}' does not exist.")
        sys.exit(1)

    setup_db = SetupDatabase(db_path, sql_script)
    setup_db.setup()