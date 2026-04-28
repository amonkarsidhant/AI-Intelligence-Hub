FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY fetch_news.py dashboard_new.py scoring_engine.py data_models.py digest_generator.py config.json ./
COPY config ./config
COPY requirements.txt ./
COPY templates ./templates
COPY static ./static

RUN mkdir -p /app/data/cache /app/data/digests && pip install --no-cache-dir -r requirements.txt

EXPOSE 8888

ENV DATA_DIR=/app/data
ENV DIGEST_DIR=/app/data/digests
ENV DATA_FILE=/app/data/data.json
ENV SCORED_DATA_FILE=/app/data/data_scored.json
ENV CACHE_DIR=/app/data/cache
ENV DB_PATH=/app/data/intelligence.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8888/ || exit 1

CMD ["gunicorn", "-b", "0.0.0.0:8888", "-w", "2", "--timeout", "180", "dashboard_new:app"]
