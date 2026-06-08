import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from google.cloud import bigquery
from google.api_core.exceptions import Conflict
from src.bigquery.client import get_bq_client
from src.bigquery.schemas import MATCH_RAW_SCHEMA

DATASET_ID = "lol_bronze"
LOCATION = "US"  # or "asia-southeast1" for SG region


def create_dataset(client: bigquery.Client) -> bigquery.Dataset:
    dataset_ref = bigquery.DatasetReference(client.project, DATASET_ID)
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = LOCATION
    dataset.description = "Bronze layer — raw Riot Games API responses"

    try:
        dataset = client.create_dataset(dataset)
        print(f"Created dataset: {DATASET_ID}")
    except Conflict:
        print(f"Dataset already exists: {DATASET_ID}")
        dataset = client.get_dataset(dataset_ref)

    return dataset


def create_table(
    client: bigquery.Client,
    dataset: bigquery.Dataset,
    table_name: str,
    schema: list,
    partition_field: str = "ingested_at",
) -> bigquery.Table:
    table_ref = dataset.table(table_name)
    table = bigquery.Table(table_ref, schema=schema)

    # Partition by ingestion date — keeps query costs low
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field=partition_field,
    )

    # Cluster by platform and queue_id for efficient filtering
    table.clustering_fields = ["platform", "queue_id"]

    try:
        table = client.create_table(table)
        print(f"Created table: {table_name}")
    except Conflict:
        print(f"Table already exists: {table_name}")
        table = client.get_table(table_ref)

    return table


def setup_bronze_layer():
    client = get_bq_client()
    dataset = create_dataset(client)

    create_table(client, dataset, "match_raw", MATCH_RAW_SCHEMA)

    print("Bronze layer setup complete.")


if __name__ == "__main__":
    setup_bronze_layer()