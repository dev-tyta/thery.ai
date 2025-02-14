from multiprocessing import Process
from src.api import run_fastapi  # Make sure run_fastapi is importable from src/api.py
from src.tele_bot.bot import main as run_telegram_bot

if __name__ == "__main__":
    # Start the Telegram bot in a separate process
    telegram_process = Process(target=run_telegram_bot)
    telegram_process.start()

    # Start FastAPI (this will block in the main process)
    run_fastapi()

    # Optionally, wait for the Telegram process to finish
    telegram_process.join()
