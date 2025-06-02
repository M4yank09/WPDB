from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

def convert_date(ts):
    return datetime.datetime(2001, 1, 1) + datetime.timedelta(seconds=ts)

def get_messages(phone_number: str):
    conn = sqlite3.connect("ChatStorage.sqlite")
    cur = conn.cursor()
    cur.execute("""
        SELECT ZTEXT, ZISFROMME, ZMESSAGEDATE, ZPARTNERNAME 
        FROM ZWAMESSAGE 
        JOIN ZWACHATSESSION ON ZWAMESSAGE.ZCHATSESSION = ZWACHATSESSION.Z_PK 
        WHERE ZPARTNERNAME LIKE ?
        ORDER BY ZMESSAGEDATE
    """, (f"%{phone_number}%",))
    data = cur.fetchall()
    conn.close()
    return [{
        "text": row[0],
        "from_me": bool(row[1]),
        "timestamp": convert_date(row[2]).isoformat(),
        "partner": row[3]
    } for row in data if row[0]]

@app.get("/chat")
def chat(phone: str = Query(...)):
    return get_messages(phone)
