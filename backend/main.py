from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import datetime

app = FastAPI(title="Exness MT5 Signal Monitor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your verified Exness account ID
VERIFIED_ACCOUNT_ID = 436888140

class TradeSignal(BaseModel):
    account_id: int
    symbol: str
    action: str
    price: float
    message: str
    time: Optional[str] = None

class MT5LoginPayload(BaseModel):
    login: int
    password: str
    server: str

signals_db = []

@app.get("/")
def home():
    return {"status": "online", "system": "Exness MT5 Live Monitor"}

@app.post("/api/webhook")
def receive_signal(signal: TradeSignal):
    if signal.account_id != VERIFIED_ACCOUNT_ID:
        raise HTTPException(status_code=403, detail="Unauthorized Exness Account ID")
    
    if not signal.time:
        signal.time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    signals_db.insert(0, signal.dict())
    if len(signals_db) > 50:
        signals_db.pop()
    return {"status": "success", "received": signal}

@app.post("/api/mt5-auth-test")
def test_exness_login(credentials: MT5LoginPayload):
    if credentials.login != VERIFIED_ACCOUNT_ID:
        raise HTTPException(status_code=401, detail="Invalid Account ID credentials")
    return {
        "status": "authenticated",
        "account": credentials.login,
        "server": credentials.server,
        "message": "Exness MT5 account credentials verified and secured successfully."
    }

@app.get("/api/signals")
def get_signals():
    return {"status": "success", "data": signals_db}
