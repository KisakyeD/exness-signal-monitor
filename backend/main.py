from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

signal_cache = []

class TradeSignal(BaseModel):
    symbol: str
    action: str
    price: float
    message: Optional[str] = "Exness Alert"

@app.get("/")
def home():
    return {"status": "online", "service": "Exness Mobile Signal Monitor"}

@app.post("/api/webhook")
def receive_signal(signal: TradeSignal):
    global signal_cache
    entry = signal.model_dump()
    entry["time"] = datetime.utcnow().strftime("%H:%M:%S UTC")
    signal_cache.insert(0, entry)
    if len(signal_cache) > 25:
        signal_cache.pop()
    return {"status": "success", "received": entry}

@app.get("/api/signals")
def get_signals():
    return {"status": "success", "data": signal_cache}
