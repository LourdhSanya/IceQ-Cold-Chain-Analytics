
import pandas as pd
import joblib

from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

DATA_PATH = Path("data/iceq_ml_dataset_clean_v1.csv")
OUTPUT_PATH = Path("data/iceq_anomaly_by_food_type_v1.csv")
MODEL_PATH = Path("models/iceq_anomaly_by_food_type_v1.joblib")

features = [
    "temperature_current",
    "humidity_current",
    "temperature_threshold_c",
    "temperature_margin",
    "temperature_change_5m",
    "temperature_change_15m",
    "temperature_change_30m",
    "temperature_mean_previous_30m",
    "temperature_max_previous_30m",
    "humidity_mean_previous_30m",
]

df = pd.read_csv(DATA_PATH)

df["anomaly_score"] = float("nan")
df["anomaly_label"] = 1

models = {}

for food_type in sorted(df["food_type"].unique()):
    mask = df["food_type"] == food_type
    X = df.loc[mask, features]

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("isolation_forest", IsolationForest(
            n_estimators=200,
            contamination="auto",
            random_state=42,
        )),
    ])

    model.fit(X)

    detector = model.named_steps["isolation_forest"]
    X_scaled = model.named_steps["scaler"].transform(X)

    df.loc[mask, "anomaly_score"] = detector.decision_function(
        X_scaled
    )
    df.loc[mask, "anomaly_label"] = detector.predict(X_scaled)

    models[food_type] = {
        "model": model,
        "features": features,
    }

df["is_anomaly"] = df["anomaly_label"] == -1

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_PATH, index=False)
joblib.dump(models, MODEL_PATH)

print("=== Per-Food-Type Isolation Forest ===")
print("Rows analysed:", len(df))

print("\nAnomalies by food type:")
print(
    df.groupby("food_type").agg(
        readings=("is_anomaly", "size"),
        anomalies=("is_anomaly", "sum"),
        anomaly_rate=("is_anomaly", "mean"),
    ).assign(
        anomaly_rate=lambda x: (x["anomaly_rate"] * 100).round(2)
    ).to_string()
)

print("\nSaved results:", OUTPUT_PATH)
print("Saved models:", MODEL_PATH)
