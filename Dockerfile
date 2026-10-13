FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal system dependencies required for asyncpg / psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (cache-efficient layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose default port (Heroku ignores EXPOSE and dynamically injects $PORT at runtime)
EXPOSE 8000

# Run Harvester Web Dashboard via runner script (binds dynamically to $PORT)
CMD ["python", "run_dashboard.py"]
