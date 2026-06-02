import os
import threading
import mlflow.sklearn
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

TIP_MODEL_URI = "gs://nyc-taxi-platform-2026-data/models/tip_v1"
DEMAND_MODEL_URI = "gs://nyc-taxi-platform-2026-data/models/demand_v1"

app = FastAPI(title="NYC Taxi Model Serving API")

tip_model = None
demand_model = None
models_loading = True


def load_models():
    global tip_model, demand_model, models_loading
    try:
        tip_model = mlflow.sklearn.load_model(TIP_MODEL_URI)
        print("Tip model loaded")
    except Exception as e:
        print(f"Error loading tip model: {e}")
    try:
        demand_model = mlflow.sklearn.load_model(DEMAND_MODEL_URI)
        print("Demand model loaded")
    except Exception as e:
        print(f"Error loading demand model: {e}")
    models_loading = False


@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=load_models, daemon=True)
    thread.start()


class TipRequest(BaseModel):
    total_trips: float
    avg_fare: float
    avg_distance: float
    avg_duration_minutes: float


class DemandRequest(BaseModel):
    avg_fare: float
    avg_distance: float
    avg_duration_minutes: float
    total_revenue: float


@app.get("/health")
def health():
    return {
        "status": "ok",
        "tip_model_loaded": tip_model is not None,
        "demand_model_loaded": demand_model is not None,
        "models_loading": models_loading,
    }


@app.post("/predict/tip")
def predict_tip(request: TipRequest):
    if tip_model is None:
        raise HTTPException(status_code=503, detail="Tip model not loaded")
    features = pd.DataFrame([{
        "total_trips": request.total_trips,
        "avg_fare": request.avg_fare,
        "avg_distance": request.avg_distance,
        "avg_duration_minutes": request.avg_duration_minutes,
    }])
    prediction = tip_model.predict(features)[0]
    return {"predicted_avg_tip": round(float(prediction), 4)}


@app.post("/predict/demand")
def predict_demand(request: DemandRequest):
    if demand_model is None:
        raise HTTPException(status_code=503, detail="Demand model not loaded")
    features = pd.DataFrame([{
        "avg_fare": request.avg_fare,
        "avg_distance": request.avg_distance,
        "avg_duration_minutes": request.avg_duration_minutes,
        "total_revenue": request.total_revenue,
    }])
    prediction = demand_model.predict(features)[0]
    probability = demand_model.predict_proba(features)[0][1]
    return {
        "high_demand": bool(prediction),
        "probability": round(float(probability), 4),
    }