import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from datetime import datetime
from feast import FeatureStore
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings("ignore")

FEAST_REPO_PATH = "E:/IP/nyc-taxi-platform/feast/nyc_taxi_features/feature_repo"
MLFLOW_TRACKING_URI = "http://localhost:5000"

def build_entity_df():
    zones = list(range(1, 263))
    months = [
        datetime(2022, 1, 1), datetime(2022, 2, 1), datetime(2022, 3, 1),
        datetime(2022, 4, 1), datetime(2022, 5, 1), datetime(2022, 6, 1),
        datetime(2022, 7, 1), datetime(2022, 8, 1), datetime(2022, 9, 1),
        datetime(2022, 10, 1), datetime(2022, 11, 1), datetime(2022, 12, 1),
    ]
    rows = []
    for zone in zones:
        for month in months:
            rows.append({"pickup_location_id": zone, "trip_timestamp": month})
    return pd.DataFrame(rows)

def fetch_features(store, entity_df):
    df = store.get_historical_features(
        entity_df=entity_df,
        features=[
            "zone_daily_stats:total_trips",
            "zone_daily_stats:total_revenue",
            "zone_daily_stats:avg_fare",
            "zone_daily_stats:avg_distance",
            "zone_daily_stats:avg_duration_minutes",
        ]
    ).to_df()
    df = df.dropna()
    numeric_cols = ["total_trips", "total_revenue", "avg_fare", "avg_distance", "avg_duration_minutes"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna()
    return df

def train_tip_model(df):
    df["avg_tip"] = df["total_revenue"] / df["total_trips"] * 0.15

    features = ["total_trips", "avg_fare", "avg_distance", "avg_duration_minutes"]
    X = df[features]
    y = df["avg_tip"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    mlflow.set_experiment("tip_prediction")

    with mlflow.start_run(run_name="random_forest_tip"):
        params = {"n_estimators": 100, "max_depth": 6, "random_state": 42}
        model = RandomForestRegressor(**params)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        mlflow.log_params(params)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            registered_model_name="tip_predictor"
        )

        print(f"Tip model -- MAE: {mae:.4f}, R2: {r2:.4f}")
        return model

def train_demand_model(df):
    threshold = df["total_trips"].median()
    df["high_demand"] = (df["total_trips"] > threshold).astype(int)

    features = ["avg_fare", "avg_distance", "avg_duration_minutes", "total_revenue"]
    X = df[features]
    y = df["high_demand"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    mlflow.set_experiment("high_demand_classification")

    with mlflow.start_run(run_name="random_forest_demand"):
        params = {"n_estimators": 100, "max_depth": 6, "random_state": 42}
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds)

        mlflow.log_params(params)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            registered_model_name="high_demand_classifier"
        )

        print(f"Demand model -- Accuracy: {acc:.4f}, F1: {f1:.4f}")
        return model

if __name__ == "__main__":
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    store = FeatureStore(repo_path=FEAST_REPO_PATH)

    print("Building entity dataframe...")
    entity_df = build_entity_df()

    print("Fetching features from Feast offline store...")
    df = fetch_features(store, entity_df)
    print(f"Training data shape: {df.shape}")

    print("Training tip prediction model...")
    train_tip_model(df)

    print("Training high demand classification model...")
    train_demand_model(df)

    print("Done. Check MLflow UI at http://localhost:5000")