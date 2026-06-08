from google.cloud import bigquery
from src.bigquery.client import get_bq_client
import json
import io
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)


def _match_exists(client: bigquery.Client, table_id: str, match_id: str) -> bool:
    """Returns True if match_id already exists in the table."""
    query = f"""
        SELECT 1
        FROM `{table_id}`
        WHERE match_id = @match_id
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("match_id", "STRING", match_id)]
    )
    results = client.query(query, job_config=job_config).result()
    return any(True for _ in results)


def insert_match_to_bronze(raw_payload: dict):
    client = get_bq_client()
    table_id = f"{client.project}.lol_bronze.match_raw"

    # Extract catalog fields from payload to keep the lake queryable
    info = raw_payload.get("info", {})
    metadata = raw_payload.get("metadata", {})
    game_start_ms = info.get("gameStartTimestamp")

    row = {
        "match_id": metadata.get("matchId"),
        "data_version": metadata.get("dataVersion"),
        "queue_id": info.get("queueId"),
        "game_version": info.get("gameVersion"),
        "game_start_timestamp": (
            datetime.fromtimestamp(game_start_ms / 1000, tz=timezone.utc).isoformat()
            if game_start_ms else None
        ),
        "raw_payload": json.dumps(raw_payload),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "platform": info.get("platformId"),  # e.g. "SEA"
    }

    logger.info(f"Inserting match raw data: {row['match_id']} | queue={row['queue_id']} | patch={row['game_version']}")

    data = json.dumps(row) + "\n"
    file_obj = io.BytesIO(data.encode("utf-8"))

    if _match_exists(client, table_id, row["match_id"]):
        logger.info(f"Skipping duplicate match: {row['match_id']} — already exists in {table_id}")
        return

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,  # append, don't overwrite
    )

    load_job = client.load_table_from_file(file_obj, table_id, job_config=job_config)
    load_job.result()

    logger.info(f"Loaded match {row['match_id']} into {table_id}")