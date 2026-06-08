import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from google.cloud import bigquery
import dotenv

dotenv.load_dotenv()

def get_bq_client() -> bigquery.Client:
    project_id = os.environ["GCP_PROJECT_ID"]
    return bigquery.Client(project=project_id)