import joblib
import json
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "marathon_model.pkl")
FEATURE_PATH = os.path.join(os.path.dirname(__file__), "model", "feature_names.json")

_model = None
_feature_info = None

def load_model():
    global _model, _feature_info
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        with open(FEATURE_PATH) as f:
            _feature_info = json.load(f)
    return _model, _feature_info

def minutes_to_hms(minutes: float) -> str:
    total_seconds = int(round(minutes * 60))
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h}:{m:02d}:{s:02d}"

def pace_to_mmss(pace_min_per_mile: float) -> str:
    total_seconds = int(round(pace_min_per_mile * 60))
    m = total_seconds // 60
    s = total_seconds % 60
    return f"{m}:{s:02d}"

def compute_splits(total_minutes: float):
    marathon_km = 42.195
    checkpoints = [
        ("5K", 5),
        ("10K", 10),
        ("15K", 15),
        ("20K", 20),
        ("Half", 21.0975),
        ("25K", 25),
        ("30K", 30),
        ("35K", 35),
        ("40K", 40),
        ("Finish", 42.195),
    ]
    splits = []
    for label, km in checkpoints:
        frac = km / marathon_km
        split_min = total_minutes * frac
        splits.append({"label": label, "time": minutes_to_hms(split_min)})
    return splits

def predict(data: dict) -> dict:
    model, feature_info = load_model()
    feature_names = feature_info["feature_names"]
    importances = feature_info["feature_importances"]

    gender_map = {"M": 1, "F": 0, "NB": 0}
    gender_val = gender_map.get(data.get("gender", "M"), 0)

    row = [
        data.get("age", 35),
        gender_val,
        data.get("weight_lbs", 155),
        data.get("height_inches", 68),
        data.get("weekly_mileage", 30),
        data.get("long_run_miles", 16),
        data.get("avg_pace_min_per_mile", 10.0),
        data.get("runs_per_week", 4),
        data.get("weeks_training", 16),
        data.get("cross_training_hours", 0),
        int(data.get("first_marathon", False)),
        data.get("previous_marathons", 0),
        data.get("half_marathon_pr_minutes") or -1,
        data.get("ten_k_pr_minutes") or -1,
        data.get("five_k_pr_minutes") or -1,
    ]

    X = np.array([row])
    predicted_minutes = float(model.predict(X)[0])
    predicted_minutes = max(120, min(480, predicted_minutes))

    # Confidence range ±15 min
    low = predicted_minutes - 15
    high = predicted_minutes + 15

    # Pace per mile
    pace = predicted_minutes / 26.2191

    # vs average (4:29:53 = 269.88 min)
    avg_minutes = 269.88
    diff = avg_minutes - predicted_minutes
    sign = "faster" if diff > 0 else "slower"
    abs_diff = abs(diff)
    diff_str = f"{minutes_to_hms(abs_diff)} {sign} than average"

    # Top features
    sorted_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:5]
    readable_names = {
        "avg_pace_min_per_mile": "Avg Training Pace",
        "weekly_mileage": "Weekly Mileage",
        "long_run_miles": "Longest Run",
        "half_marathon_pr_minutes": "Half Marathon PR",
        "age": "Age",
        "gender": "Gender",
        "weight_lbs": "Weight",
        "height_inches": "Height",
        "runs_per_week": "Runs Per Week",
        "weeks_training": "Weeks Training",
        "cross_training_hours": "Cross Training",
        "first_marathon": "First Marathon",
        "previous_marathons": "Marathons Completed",
        "ten_k_pr_minutes": "10K PR",
        "five_k_pr_minutes": "5K PR",
    }
    top_features = [
        {"name": readable_names.get(k, k), "importance": round(v * 100, 1)}
        for k, v in sorted_features
    ]

    return {
        "predicted_minutes": round(predicted_minutes, 1),
        "predicted_time": minutes_to_hms(predicted_minutes),
        "pace_per_mile": pace_to_mmss(pace),
        "confidence_low": minutes_to_hms(low),
        "confidence_high": minutes_to_hms(high),
        "vs_average": diff_str,
        "splits": compute_splits(predicted_minutes),
        "top_features": top_features,
    }
