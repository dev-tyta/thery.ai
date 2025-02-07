from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
import schedule
import time
import requests
import threading
import asyncio
import uvicorn
from multiprocessing import Process

from src.llm.routes import router as conversation_router
from src.tele_bot.bot import main as run_telegram_bot
from src.llm.core.config import settings
from src.llm.agents.conversation_agent import ConversationAgent

def on_startup():
    global conversation_agent
    conversation_agent = ConversationAgent()

    
app = FastAPI(
    title="TheryAI API",
    description="API for TheryAI",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=True,
    on_startup=[on_startup]
)



app.include_router(conversation_router)

@app.get("/")
async def home():
    return {"message": "Welcome to TheryAI API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

def ping_server():
    try:
        print("Pinging server")
        response = requests.get("https://theryai-api./")
    except requests.exceptions.RequestException as e:
        print("Server is down")
        # send email to admin
    
schedule.every(10).minutes.do(ping_server)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


thread = threading.Thread(target=run_schedule)
thread.daemon = True
thread.start()


def run_bot():
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
    )

def run_telegram_bot():
    asyncio(run_telegram_bot())


if __name__ == "__main__":
    fastapi_process = Process(target=run_bot)
    telegram_process = Process(target=run_telegram_bot)
    
    fastapi_process.start()
    telegram_process.start()

    fastapi_process.join()
    telegram_process.join()
    