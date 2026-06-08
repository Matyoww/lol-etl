import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from google.cloud import bigquery
from client import get_bq_client

DATASET_ID = "lol_bronze"

def reset_bronze_layer():
    client = get_bq_client()
    dataset_ref = bigquery.DatasetReference(client.project, DATASET_ID)

    try:
        client.delete_dataset(dataset_ref, delete_contents=True)
        print(f"Deleted dataset: {DATASET_ID}")
    except Exception as e:
        print(f"Error deleting dataset: {e}")


if __name__ == "__main__":
    reset_bronze_layer()