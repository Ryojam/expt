from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import json
from threading import Lock

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------
# 状態
# ------------------
bet_open = True
lock = Lock()

ADMIN_TOKEN = "keiba2026-admin"
HORSES = ["A", "B", "C", "D", "E"]

# ------------------
# DB
# ------------------
def init_db():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        point INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        horse TEXT,
        amount INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS race_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        winner TEXT,
        result TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ------------------
# adminチェック
# ------------------
def check_admin(token: str):
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="unauthorized")

# ------------------
# ユーザー作成
# ------------------
@app.post("/create_user/{name}")
def create_user(name: str):
    if not name.strip():
        return {"error": "名前を入力してください"}

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE name = ?", (name,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO users (name, point) VALUES (?, ?)", (name, 100))

    conn.commit()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    conn.close()

    return {"users": users}

# ------------------
# ベット
# ------------------
class BetRequest(BaseModel):
    name: str
    horse: str
    amount: int


@app.post("/bet")
def bet(req: BetRequest):
    global bet_open

    if not bet_open:
        return {"error": "ベットは締切中です"}

    if req.amount <= 0:
        return {"error": "1ポイント以上"}

    if req.horse not in HORSES:
        return {"error": "無効な馬"}

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute("SELECT point FROM users WHERE name = ?", (req.name,))
    row = cur.fetchone()

    if not row:
        return {"error": "ユーザーなし"}

    if row[0] < req.amount:
        return {"error": "ポイント不足"}

    cur.execute("""
        INSERT INTO bets (name, horse, amount)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
        horse=excluded.horse,
        amount=excluded.amount
    """, (req.name, req.horse, req.amount))

    cur.execute("UPDATE users SET point = point - ? WHERE name = ?", (req.amount, req.name))

    conn.commit()
    conn.close()

    return {"ok": True}

# ------------------
# ベット解除
# ------------------
@app.post("/cancel_bet")
def cancel_bet(req: dict):
    name = req.get("name")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute("SELECT amount FROM bets WHERE name = ?", (name,))
    row = cur.fetchone()

    if not row:
        return {"error": "なし"}

    amount = row[0]

    cur.execute("UPDATE users SET point = point + ? WHERE name = ?", (amount, name))
    cur.execute("DELETE FROM bets WHERE name = ?", (name,))

    conn.commit()
    conn.close()

    return {"ok": True}

# ------------------
# レース（★完全版）
# ------------------
@app.post("/race")
def race(req: dict):
    check_admin(req.get("token"))

    winner = req.get("winner")
    global bet_open

    if winner not in HORSES:
        return {"error": "無効な馬"}

    with lock:
        conn = sqlite3.connect("app.db")
        cur = conn.cursor()

        cur.execute("SELECT name, horse, amount FROM bets")
        bets = cur.fetchall()

        if not bets:
            return {"error": "ベットなし"}

        totals = {}
        for _, horse, amount in bets:
            totals[horse] = totals.get(horse, 0) + amount

        total_all = sum(totals.values())

        results = []

        for name, horse, amount in bets:
            if horse == winner and totals.get(horse, 0) > 0:
                odds = total_all / totals[horse]
                win = int(amount * odds)

                cur.execute(
                    "UPDATE users SET point = point + ? WHERE name = ?",
                    (win, name)
                )

                results.append({
                    "name": name,
                    "result": "WIN",
                    "win": win,
                    "odds": round(odds, 2)
                })
            else:
                results.append({
                    "name": name,
                    "result": "LOSE",
                    "win": 0
                })

        cur.execute(
            "INSERT INTO race_history (winner, result) VALUES (?, ?)",
            (winner, json.dumps(results))
        )

        cur.execute("DELETE FROM bets")

        conn.commit()
        conn.close()

        return {"winner": winner, "result": results}

# ------------------
# 一覧
# ------------------
@app.get("/users")
def users():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    return {"users": cur.fetchall()}


@app.get("/bets")
def bets():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM bets")
    return {"bets": cur.fetchall()}


@app.get("/ranking")
def ranking():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute("SELECT name, point FROM users ORDER BY point DESC")
    rows = cur.fetchall()

    return {
        "ranking": [
            {"rank": i+1, "name": r[0], "point": r[1]}
            for i, r in enumerate(rows)
        ]
    }

# ------------------
# オッズ
# ------------------
@app.get("/popularity")
def popularity():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    cur.execute("SELECT horse, amount FROM bets")
    bets = cur.fetchall()

    stats = {}
    total = 0

    for h, a in bets:
        total += a
        stats[h] = stats.get(h, 0) + a

    result = []

    for h in HORSES:
        a = stats.get(h, 0)
        percent = round(a / total * 100, 1) if total else 0
        odds = round(total / a, 2) if a else 0

        result.append({
            "horse": h,
            "amount": a,
            "percent": percent,
            "odds": odds
        })

    result.sort(key=lambda x: x["amount"], reverse=True)

    return {"total_bet": total, "popularity": result}

# ------------------
# 管理API（完全ロック）
# ------------------
@app.post("/admin/bet_close")
def close_bet(req: dict):
    check_admin(req.get("token"))

    global bet_open
    with lock:
        bet_open = False

    return {"bet_open": bet_open}


@app.post("/admin/bet_open")
def open_bet(req: dict):
    check_admin(req.get("token"))

    global bet_open
    with lock:
        bet_open = True

    return {"bet_open": bet_open}

@app.post("/admin/login")
def admin_login(req: dict):
    return {"ok": req.get("pass") == "keiba2026"}

@app.get("/bet_status")
def status():
    return {"bet_open": bet_open}

# ------------------
# HTML
# ------------------
@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    token = request.query_params.get("token")

    if token != ADMIN_TOKEN:
        return HTMLResponse("403 Forbidden", status_code=403)

    with open("admin.html", "r", encoding="utf-8") as f:
        return f.read()