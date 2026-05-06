import os
import sys
import logging
from interface.database import  PostgreSQLClient
from src.set_environment import set_environment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    set_environment()

    sql_script = os.getenv('RESET_SQL')
    if not os.path.exists(sql_script):
        logger.error(f"SQL script '{sql_script}' does not exist.")
        sys.exit(1)

    db_client = PostgreSQLClient()
    try:
        db_client.open_connection()
        with open(sql_script, 'r') as file:
            sql_script_content = file.read()
        db_client.execute_script(sql_script_content)
        logger.info("Database reset completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during database reset: {e}")
    finally:
        db_client.close_connection()
        logger.info("Database connection closed after reset.")