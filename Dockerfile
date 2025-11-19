# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies directly with pip
# Using specific versions from pyproject.toml
RUN pip install --no-cache-dir \
    pandas==2.2.3 \
    python-dotenv==1.0.1 \
    requests==2.32.3

# Copy source code
COPY src/ ./src/

# Create output directory for player matches
RUN mkdir -p /app/player_matches

# Set Python path to find modules
ENV PYTHONPATH=/app

# Set environment variables (can be overridden at runtime)
ENV PERSONAL_API_KEY=""
ENV PERSONAL_GAME_NAME=""
ENV PERSONAL_TAGLINE=""

# Run the extract script
CMD ["python", "-m", "src.extract"]
