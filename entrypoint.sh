#!/bin/bash
set -e

echo "Starting Redis server..."
# Start Redis in the background
redis-server &

echo "Starting Telegram bot..."
# Start the Telegram bot in the background
python -m src.tele_bot.bot &

echo "Starting FastAPI application..."
# Start FastAPI with Uvicorn
exec uvicorn app.src.api:app --host 0.0.0.0 --port 7860 --workers 1
