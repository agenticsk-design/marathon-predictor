from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from predictor import predict
from auth import (
    get_db, init_users_table, hash_password, verify_password,
    create_token, get_current_user
)
import sqlite3, os, time

app = FastAPI(title="Marathon Time Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB init ---

def init_db():
    init_users_table()
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS training_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            week INTEGER NOT NULL,
            mileage REAL,
            long_run REAL,
            key_workout TEXT,
            created_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

# --- Auth models ---

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# --- Prediction model ---

class RunnerInput(BaseModel):
    age: int
    gender: str
    weight_lbs: float
    height_inches: float
    weekly_mileage: float
    long_run_miles: float
    avg_pace_min_per_mile: float
    runs_per_week: int
    weeks_training: int
    cross_training_hours: float = 0
    first_marathon: bool = False
    previous_marathons: int = 0
    half_marathon_pr_minutes: Optional[float] = None
    ten_k_pr_minutes: Optional[float] = None
    five_k_pr_minutes: Optional[float] = None

# --- Training log models ---

class TrainingWeek(BaseModel):
    week: int
    mileage: Optional[float] = None
    long_run: Optional[float] = None
    key_workout: Optional[str] = None

class TrainingLogSave(BaseModel):
    rows: List[TrainingWeek]

# --- Routes ---

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/register")
def register(body: RegisterRequest):
    conn = get_db()
    try:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (body.email.lower(),)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        if len(body.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        hashed = hash_password(body.password)
        cursor = conn.execute(
            "INSERT INTO users (email, hashed_password, created_at) VALUES (?, ?, ?)",
            (body.email.lower(), hashed, int(time.time()))
        )
        conn.commit()
        token = create_token(cursor.lastrowid, body.email.lower())
        return {"token": token, "email": body.email.lower()}
    finally:
        conn.close()

@app.post("/auth/login")
def login(body: LoginRequest):
    conn = get_db()
    try:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (body.email.lower(),)).fetchone()
        if not user or not verify_password(body.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        token = create_token(user["id"], user["email"])
        return {"token": token, "email": user["email"]}
    finally:
        conn.close()

@app.get("/auth/me")
def me(current_user=Depends(get_current_user)):
    return {"id": current_user["id"], "email": current_user["email"]}

@app.post("/predict")
def predict_marathon(runner: RunnerInput):
    try:
        result = predict(runner.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/training-log")
def save_training_log(payload: TrainingLogSave, current_user=Depends(get_current_user)):
    conn = get_db()
    try:
        conn.execute("DELETE FROM training_logs WHERE user_id = ?", (current_user["id"],))
        now = int(time.time())
        conn.executemany(
            "INSERT INTO training_logs (user_id, week, mileage, long_run, key_workout, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            [(current_user["id"], r.week, r.mileage, r.long_run, r.key_workout, now) for r in payload.rows]
        )
        conn.commit()
        return {"status": "saved", "rows": len(payload.rows)}
    finally:
        conn.close()

@app.get("/training-log")
def get_training_log(current_user=Depends(get_current_user)):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT week, mileage, long_run, key_workout FROM training_logs WHERE user_id = ? ORDER BY week",
            (current_user["id"],)
        ).fetchall()
        return {"rows": [dict(r) for r in rows]}
    finally:
        conn.close()

@app.delete("/training-log")
def delete_training_log(current_user=Depends(get_current_user)):
    conn = get_db()
    try:
        conn.execute("DELETE FROM training_logs WHERE user_id = ?", (current_user["id"],))
        conn.commit()
        return {"status": "deleted"}
    finally:
        conn.close()
