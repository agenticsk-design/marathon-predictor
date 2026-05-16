"""
Train a GradientBoostingRegressor to predict marathon finish times.
Generates synthetic training data based on physiological formulas.
"""
import numpy as np
import pandas as pd
import joblib
import json
import os

np.random.seed(42)
N = 2000

def riegel(pr_distance_km, pr_minutes, target_distance_km=42.195):
    """Riegel formula: T2 = T1 * (D2/D1)^1.06"""
    return pr_minutes * (target_distance_km / pr_distance_km) ** 1.06

def age_grade_factor(age):
    """Returns slowdown multiplier. 1.0 = peak (ages 25-35)."""
    if age < 20:
        return 1.04
    elif age <= 35:
        return 1.0
    elif age <= 40:
        return 1.02
    elif age <= 45:
        return 1.05
    elif age <= 50:
        return 1.09
    elif age <= 55:
        return 1.14
    elif age <= 60:
        return 1.20
    else:
        return 1.28

def generate_dataset(n=N):
    rows = []
    for _ in range(n):
        age = np.random.randint(18, 70)
        gender = np.random.choice([0, 1], p=[0.45, 0.55])  # 0=F, 1=M
        weight_lbs = np.random.normal(155 if gender == 1 else 135, 25)
        weight_lbs = np.clip(weight_lbs, 90, 280)
        height_inches = np.random.normal(70 if gender == 1 else 65, 3)
        height_inches = np.clip(height_inches, 58, 80)

        weekly_mileage = np.random.normal(35, 15)
        weekly_mileage = np.clip(weekly_mileage, 10, 100)

        long_run_miles = np.clip(np.random.normal(16, 4), 8, 26.2)
        avg_pace = np.clip(np.random.normal(10.0, 1.5), 6.0, 16.0)
        runs_per_week = np.random.randint(3, 8)
        weeks_training = np.random.randint(8, 24)
        cross_training_hours = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.3, 0.2, 0.2, 0.15, 0.1, 0.05])
        first_marathon = np.random.choice([0, 1], p=[0.65, 0.35])
        previous_marathons = 0 if first_marathon else np.random.randint(1, 15)

        # Generate PRs (not all runners have them)
        has_half = np.random.random() > 0.4
        has_10k = np.random.random() > 0.5
        has_5k = np.random.random() > 0.45

        half_pr = np.random.normal(115, 25) if has_half else None
        ten_k_pr = np.random.normal(55, 12) if has_10k else None
        five_k_pr = np.random.normal(26, 6) if has_5k else None

        if half_pr: half_pr = max(70, half_pr)
        if ten_k_pr: ten_k_pr = max(35, ten_k_pr)
        if five_k_pr: five_k_pr = max(16, five_k_pr)

        # --- Compute target marathon time ---
        # Base: from avg pace (most direct predictor)
        # Marathon is 26.2 miles; apply fatigue factor ~1.08x
        base_time = avg_pace * 26.2 * 1.08

        # Mileage adjustment: higher mileage = better endurance
        mileage_adj = -0.5 * (weekly_mileage - 35)  # -0.5 min per extra mile/week
        mileage_adj = np.clip(mileage_adj, -15, 20)

        # Long run adjustment
        long_run_adj = -0.3 * (long_run_miles - 16)
        long_run_adj = np.clip(long_run_adj, -8, 8)

        # Age grading
        age_mult = age_grade_factor(age)

        # Gender factor (M ~8% faster on average)
        gender_mult = 0.93 if gender == 1 else 1.0

        # Experience
        exp_bonus = 5 if first_marathon else max(0, 10 - previous_marathons * 1.5)

        # Riegel override if half PR available (most accurate)
        if half_pr:
            riegel_time = riegel(21.0975, half_pr) * age_mult * gender_mult
            base_time = 0.6 * riegel_time + 0.4 * (base_time * age_mult * gender_mult)
        elif ten_k_pr:
            riegel_time = riegel(10, ten_k_pr) * age_mult * gender_mult
            base_time = 0.4 * riegel_time + 0.6 * (base_time * age_mult * gender_mult)
        elif five_k_pr:
            riegel_time = riegel(5, five_k_pr) * age_mult * gender_mult
            base_time = 0.3 * riegel_time + 0.7 * (base_time * age_mult * gender_mult)
        else:
            base_time = base_time * age_mult * gender_mult

        marathon_time = base_time + mileage_adj + long_run_adj + exp_bonus
        marathon_time += np.random.normal(0, 8)  # noise
        marathon_time = np.clip(marathon_time, 120, 480)  # 2h to 8h range

        rows.append({
            "age": age,
            "gender": gender,
            "weight_lbs": weight_lbs,
            "height_inches": height_inches,
            "weekly_mileage": weekly_mileage,
            "long_run_miles": long_run_miles,
            "avg_pace_min_per_mile": avg_pace,
            "runs_per_week": runs_per_week,
            "weeks_training": weeks_training,
            "cross_training_hours": cross_training_hours,
            "first_marathon": int(first_marathon),
            "previous_marathons": previous_marathons,
            "half_marathon_pr_minutes": half_pr if half_pr else -1,
            "ten_k_pr_minutes": ten_k_pr if ten_k_pr else -1,
            "five_k_pr_minutes": five_k_pr if five_k_pr else -1,
            "marathon_minutes": marathon_time,
        })

    return pd.DataFrame(rows)

def train():
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error

    print("Generating synthetic training data...")
    df = generate_dataset(N)

    feature_cols = [
        "age", "gender", "weight_lbs", "height_inches",
        "weekly_mileage", "long_run_miles", "avg_pace_min_per_mile",
        "runs_per_week", "weeks_training", "cross_training_hours",
        "first_marathon", "previous_marathons",
        "half_marathon_pr_minutes", "ten_k_pr_minutes", "five_k_pr_minutes",
    ]

    X = df[feature_cols]
    y = df["marathon_minutes"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training GradientBoostingRegressor...")
    model = GradientBoostingRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        random_state=42,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    print(f"Test MAE: {mae:.1f} minutes ({mae/60:.2f} hours)")

    # Save model
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    model_path = os.path.join(os.path.dirname(__file__), "marathon_model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

    # Save feature names and importances
    feature_info = {
        "feature_names": feature_cols,
        "feature_importances": dict(zip(feature_cols, model.feature_importances_.tolist()))
    }
    info_path = os.path.join(os.path.dirname(__file__), "feature_names.json")
    with open(info_path, "w") as f:
        json.dump(feature_info, f, indent=2)
    print(f"Feature info saved to {info_path}")
    print("Done!")

if __name__ == "__main__":
    train()
