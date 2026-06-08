from google.cloud import bigquery

# Raw match data exactly as returned by Riot API
MATCH_RAW_SCHEMA = [
    bigquery.SchemaField("match_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("data_version", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("queue_id", "INTEGER", mode="NULLABLE"),       # e.g. 420 = Ranked Solo, 450 = ARAM
    bigquery.SchemaField("game_version", "STRING", mode="NULLABLE"),    # patch, e.g. "14.10.xxx"
    bigquery.SchemaField("game_start_timestamp", "TIMESTAMP", mode="NULLABLE"),  # when the game was played
    bigquery.SchemaField("raw_payload", "JSON", mode="REQUIRED"),       # full API response
    bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="REQUIRED"),  # partition key
    bigquery.SchemaField("platform", "STRING", mode="NULLABLE"),        # e.g. "SEA"
]