from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from predictor import predict

app = FastAPI(title="Marathon Time Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
