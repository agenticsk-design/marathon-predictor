# 🏃 Marathon Time Predictor

ML-powered app that forecasts your marathon finish time based on training data and demographics.

## Features
- 3-step runner input form (demographics → training data → race history)
- Gradient Boosting ML model trained on 2000 synthetic runner samples (~10 min accuracy)
- Predicted finish time with confidence range
- Pacing plan with splits at every 5K checkpoint
- Feature importance chart showing what drove the prediction
- Training log for week-by-week mileage tracking

## Quick Start

```bash
./start.sh
```

Then open **http://localhost:3000**

The script will:
1. Create a Python venv and install backend deps
2. Train the ML model (takes ~10 seconds)
3. Start the FastAPI backend on port 8000
4. Install frontend deps and start Vite on port 3000

## Manual Start

**Backend:**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python model/train.py  # only needed once
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Stack
- **Frontend:** React 18 + Vite + Tailwind CSS
- **Backend:** FastAPI + scikit-learn + joblib
- **Model:** GradientBoostingRegressor (Test MAE: ~10 min)
