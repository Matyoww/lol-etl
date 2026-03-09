import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from utils import log_function_call
# from prefect import flow, task
# from prefect.logging import get_run_logger
from src.set_environment import set_environment
from interface.database import SQLiteClient, PostgreSQLClient, DatabaseClient

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SetupDatabase:
    def __init__(self, sql_script: str, db_client: DatabaseClient = None, logger=None):
        self.db_client = db_client
        self.sql_script = sql_script
        # self.logger = get_run_logger()

    # @task
    def setup(self):
        # logger = self.logger
        try:
            self.db_client.open_connection()

            with open(self.sql_script, 'r') as file:
                sql_script_content = file.read()

            self.db_client.execute_script(sql_script_content)
            logger.info("Database setup completed successfully.")
        except Exception as e:
            logger.error(f"An error occurred during database setup: {e}")
        finally:
            self.db_client.close_connection()
            logger.info("Database connection closed.")

# @flow(name="setup_database_flow")
# @log_function_call()
def main():
    # logger = get_run_logger()
    set_environment()

    sql_script = os.getenv('SETUP_SQL')

    if not os.path.exists(sql_script):
        logger.error(f"SQL script '{sql_script}' does not exist.")
        sys.exit(1)

    setup_db = SetupDatabase(sql_script, db_client=PostgreSQLClient(), logger=logger)
    setup_db.setup()

if __name__ == "__main__":
    main()
    # main.serve(
    #     name="setup_db",
    # )
