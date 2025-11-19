# League of Legends ETL - Extract Process

This repository contains an ETL (Extract, Transform, Load) pipeline for League of Legends match data using the Riot Games API.

## Extract Process

The extract process (`src/extract.py`) retrieves match data from the Riot API for a specific player and saves it to a CSV file.

### Features

- Fetches player PUUID by Riot ID (game name and tagline)
- Retrieves match history (up to 90 matches)
- Extracts detailed match data for each game
- Saves player match data to CSV format

## Docker Usage

A Dockerfile is provided to run the extract process in a containerized environment.

### Building the Docker Image

```bash
docker build -t lol-etl-extract .
```

### Running the Container

You need to provide three environment variables to run the extract process:

1. `PERSONAL_API_KEY`: Your Riot Games API key
2. `PERSONAL_GAME_NAME`: Your League of Legends game name
3. `PERSONAL_TAGLINE`: Your League of Legends tagline

#### Using environment variables:

```bash
docker run \
  -e PERSONAL_API_KEY="your-api-key" \
  -e PERSONAL_GAME_NAME="your-game-name" \
  -e PERSONAL_TAGLINE="your-tagline" \
  -v $(pwd)/player_matches:/app/player_matches \
  lol-etl-extract
```

#### Using an .env file:

Create a `.env` file with your credentials:

```env
PERSONAL_API_KEY=your-api-key
PERSONAL_GAME_NAME=your-game-name
PERSONAL_TAGLINE=your-tagline
```

Then run:

```bash
docker run \
  --env-file .env \
  -v $(pwd)/player_matches:/app/player_matches \
  lol-etl-extract
```

### Volume Mounting

The container will output match data to `/app/player_matches` inside the container. You should mount this directory to your host system to persist the data:

```bash
-v $(pwd)/player_matches:/app/player_matches
```

This will save the CSV files to a `player_matches` directory in your current working directory.

### Using Docker Compose (Recommended)

For easier management, you can use Docker Compose:

1. Create a `.env` file with your credentials:
   ```env
   PERSONAL_API_KEY=your-api-key
   PERSONAL_GAME_NAME=your-game-name
   PERSONAL_TAGLINE=your-tagline
   ```

2. Run the extract process:
   ```bash
   docker-compose up
   ```

The output will be saved to the `player_matches` directory automatically.

## Getting a Riot API Key

1. Visit the [Riot Developer Portal](https://developer.riotgames.com/)
2. Sign in with your Riot Games account
3. Generate a development API key

Note: Development API keys expire after 24 hours and have rate limits.

## Dependencies

The Docker image includes:
- Python 3.11
- pandas 2.2.3
- python-dotenv 1.0.1
- requests 2.32.3

## Output Format

The extract process creates a CSV file named `{game_name}_{tagline}_matches.csv` in the `player_matches` directory with detailed match statistics including:
- Match ID
- Game mode
- Champion played
- KDA (Kills/Deaths/Assists)
- Gold earned
- Damage dealt
- And many more match-specific statistics

## Local Development

If you prefer to run without Docker:

1. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

2. Create a `.env` file with your credentials (see above)

3. Run the extract script:
   ```bash
   python -m src.extract
   ```
