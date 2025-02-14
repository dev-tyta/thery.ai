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
from src.llm.core.config import settings
from src.llm.agents.conversation_agent import ConversationAgent


app = FastAPI(
    title="TheryAI API",
    description="API for TheryAI",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=True,
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


def run_fastapi():
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
    )
    
if __name__ == "__main__":
    run_fastapi()