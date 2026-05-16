from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from predictor import predict
import sqlite3, os, time

app = FastAPI(title="Marathon Time Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database setup ---

DB_PATH = os.environ.get("DB_PATH", "/data/marathon.db")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS training_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            week INTEGER NOT NULL,
            mileage REAL,
            long_run REAL,
            key_workout TEXT,
            created_at INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

# --- Models ---

class RunnerInput(BaseModel):
    age: int
    gender: str  # "M", "F", "NB"
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

class TrainingWeek(BaseModel):
    week: int
    mileage: Optional[float] = None
    long_run: Optional[float] = None
    key_workout: Optional[str] = None

class TrainingLogSave(BaseModel):
    session_id: str
    rows: List[TrainingWeek]

# --- Routes ---

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict_marathon(runner: RunnerInput):
    try:
        result = predict(runner.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/training-log")
def save_training_log(payload: TrainingLogSave):
    """Save (replace) a full training log for a session."""
    conn = get_db()
    try:
        conn.execute("DELETE FROM training_logs WHERE session_id = ?", (payload.session_id,))
        now = int(time.time())
        conn.executemany(
            "INSERT INTO training_logs (session_id, week, mileage, long_run, key_workout, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            [(payload.session_id, r.week, r.mileage, r.long_run, r.key_workout, now) for r in payload.rows]
        )
        conn.commit()
        return {"status": "saved", "rows": len(payload.rows)}
    finally:
        conn.close()

@app.get("/training-log/{session_id}")
def get_training_log(session_id: str):
    """Retrieve training log for a session."""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT week, mileage, long_run, key_workout FROM training_logs WHERE session_id = ? ORDER BY week",
            (session_id,)
        ).fetchall()
        return {"session_id": session_id, "rows": [dict(r) for r in rows]}
    finally:
        conn.close()

@app.delete("/training-log/{session_id}")
def delete_training_log(session_id: str):
    """Delete all training log entries for a session."""
    conn = get_db()
    try:
        conn.execute("DELETE FROM training_logs WHERE session_id = ?", (session_id,))
        conn.commit()
        return {"status": "deleted"}
    finally:
        conn.close()
