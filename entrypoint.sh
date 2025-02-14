set -e

echo "Starting Redis server..."
# Start Redis in the background
redis-server &

echo "Starting Telegram bot..."
# Start the Telegram bot in the background (ensure __main__ in bot.py is set to run the bot)
python -m src.tele_bot.bot &

echo "Starting FastAPI application..."
# Start FastAPI with Uvicorn in the foreground so the container keeps running.
exec uvicorn app.src.api:app --host 0.0.0.0 --port 7860 --workers 1