# lol-etl

An ETL pipeline for extracting, transforming, and loading League of Legends match data using the Riot Games API into a BigQuery data lake and PostgreSQL data warehouse.

## Overview

This project pulls match history and player performance data from the Riot Games API and loads it through a medallion architecture: raw match JSON is landed in a **BigQuery Bronze layer**, then transformed and served via a **PostgreSQL Silver/Warehouse layer**. It supports multiple players and is designed to run as an Apache Airflow pipeline.

## Architecture

```mermaid
flowchart TD
    RiotAPI(["☁️ Riot Games API"])
    DataDragon(["☁️ Data Dragon API"])

    subgraph Airflow ["🌀 Apache Airflow (Docker)"]
        Extract["src/extract.py\nFetch match IDs + raw payloads"]
        PopulateDim["src/populate_dim.py\nSeed dimension tables"]
        Transform["Silver Transform\n(next layer — WIP 🚧)"]
    end

    subgraph Bronze ["🥉 Bronze — BigQuery"]
        BQ[("lol_bronze.match_raw\nRaw JSON payloads")]
    end

    subgraph Silver ["🥈 Silver — PostgreSQL (Docker)"]
        Fact[("fact_player_performances")]
        Dims[("dim_players / dim_matches\ndim_champions / dim_roles")]
    end

    RiotAPI -->|"Match data + PUUIDs"| Extract
    DataDragon -->|"Champion metadata"| PopulateDim
    Extract -->|"insert_match_to_bronze()"| BQ
    Extract -->|"INSERT facts"| Fact
    PopulateDim -->|"Seed dims"| Dims
    BQ -->|"fetch_unprocessed_matches()"| Transform
    Transform -->|"Parsed & enriched rows"| Fact
```

## Project Structure

```
├── src/                          # Core ETL logic
│   ├── extract.py                # Match extraction — calls Riot API, inserts to Bronze + Postgres
│   ├── lol_api_service.py        # Riot API handler classes (dispatch pattern)
│   ├── lol_backend_service.py    # Legacy Riot API client
│   ├── populate_dim.py           # Dimension table population (champions, roles, results)
│   ├── setup_db.py               # PostgreSQL schema setup
│   ├── reset_db.py               # Database reset utility
│   ├── set_environment.py        # Environment variable loader (.env + defaults)
│   ├── constants.py              # API cluster and endpoint enums
│   ├── utils.py                  # Shared HTTP and data helpers
│   └── bigquery/                 # BigQuery Bronze layer
│       ├── client.py             # Authenticated BigQuery client factory
│       ├── schemas.py            # BigQuery table schemas
│       ├── setup.py              # Dataset + table creation
│       ├── insert.py             # Bronze insert with duplicate guard
│       ├── fetch.py              # Bronze read — source for Silver transform
│       └── reset_bigquery.py     # Drop/recreate Bronze tables
├── interface/
│   └── database.py               # DatabaseClient abstraction (PostgreSQL + SQLite)
├── db/
│   ├── setup_pg.sql              # PostgreSQL schema DDL
│   ├── reset_pg.sql              # Drop/truncate script
│   └── setup_sqlite.sql          # SQLite schema (dev/testing)
├── static/
│   ├── champion.json             # Champion reference data
│   ├── roles.json                # Role dimension seed data
│   └── result.json               # Result dimension seed data
└── tests/                        # Test suite
```

## Database Schema

The warehouse uses a star schema centred on `fact_player_performances`:

| Table | Layer | Description |
|---|---|---|
| `lol_bronze.match_raw` | BigQuery | Raw Riot API response, one row per match |
| `fact_player_performances` | PostgreSQL | One row per player per match (kills, deaths, assists, gold, damage, vision, CS) |
| `dim_players` | PostgreSQL | Player PUUID and Riot ID |
| `dim_matches` | PostgreSQL | Match ID and game mode |
| `dim_champions` | PostgreSQL | Champion ID and name (sourced from Data Dragon) |
| `dim_roles` | PostgreSQL | Role/position lookup |
| `dim_results` | PostgreSQL | Win/loss lookup 🚧 |

### Star Schema

```mermaid
erDiagram
    fact_player_performances {
        TEXT PUUID PK
        TEXT MatchID PK
        INT RoleID FK
        INT ChampionID FK
        INT Kills
        INT Deaths
        INT Assists
        INT GoldEarned
        INT DamageDealt
        INT DamageTaken
        INT VisionScore
        INT MinionsKilled
    }
    dim_players {
        TEXT PUUID PK
        TEXT RiotIDGameName
        TEXT RiotTagLine
    }
    dim_matches {
        TEXT MatchID PK
        TEXT GameMode
    }
    dim_roles {
        SERIAL RoleID PK
        TEXT RoleName
    }
    dim_champions {
        INT ChampionID PK
        TEXT ChampionName
    }

    dim_players ||--o{ fact_player_performances : "PUUID"
    dim_matches ||--o{ fact_player_performances : "MatchID"
    dim_roles ||--o{ fact_player_performances : "RoleID"
    dim_champions ||--o{ fact_player_performances : "ChampionID"
```

## Prerequisites

- Python >= 3.12
- Docker
- Apache Airflow
- PostgreSQL instance
- Google Cloud project with BigQuery enabled + a service account key
- Riot Games API key ([obtain here](https://developer.riotgames.com/))

## Key Components

### `RiotAPI` (dispatch pattern)

`src/lol_api_service.py` implements a handler-based dispatch pattern. Each API operation is a separate class inheriting from `RiotHandler`:

- `GetPuuidByRiotId` — resolve Riot ID to PUUID
- `GetRiotIdByPuuid` — reverse PUUID lookup
- `GetMatchList` — fetch list of match IDs for a player
- `GetMatchData` — fetch full match JSON
- `GetFreeChampRotation` — fetch free champion rotation

```python
riot_api = RiotAPI(api_key)
puuid = riot_api.dispatch("GetPuuidByRiotId", "Matyoww", "3263")
matches = riot_api.dispatch("GetMatchList", "SEA", puuid, count=20)
```

### `BigQuery Bronze Layer` (`src/bigquery/`)

Raw match payloads are landed in `lol_bronze.match_raw` on every extraction run.

| Module | Purpose |
|---|---|
| `client.py` | Authenticated `bigquery.Client` factory |
| `schemas.py` | Schema definitions for Bronze tables |
| `setup.py` | Creates dataset and partitioned/clustered tables |
| `insert.py` | Inserts a raw match row; skips if `match_id` already exists |
| `fetch.py` | Reads rows from Bronze for downstream Silver processing |
| `reset_bigquery.py` | Drops and recreates Bronze tables |

### `DatabaseClient` (abstraction layer)

`interface/database.py` provides a common interface over PostgreSQL (`psycopg3`) and SQLite, making it straightforward to run the pipeline locally against SQLite or in production against PostgreSQL.

### `PopulateDim`

Dynamically reads column names from the target table and inserts seed data, supporting both in-memory data and JSON file sources with `ON CONFLICT DO NOTHING` for idempotent runs.

## Dependencies

| Package | Purpose |
|---|---|
| `apache-airflow` | Pipeline orchestration |
| `google-cloud-bigquery` | BigQuery Bronze layer client |
| `pandas` | DataFrame handling during extraction |
| `psycopg[binary]` | PostgreSQL driver |
| `requests` | HTTP calls to Riot and Data Dragon APIs |
| `pytest` | Testing |
| `coverage` | Test coverage reporting |

## Supported API Clusters

| Cluster | Base URL |
|---|---|
| `ASIA` | `https://asia.api.riotgames.com` |
| `SEA` | `https://sea.api.riotgames.com` |
| `PH2` | `https://ph2.api.riotgames.com` |

## Running Tests

```bash
pytest tests/
```

With coverage:

```bash
coverage run -m pytest tests/ && coverage report
```
