
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from pathlib import Path

# 1. Define file paths
DATA_PATH = Path("data/iceq_ml_dataset_clean_v1.csv")
OUTPUT_PATH = Path("data/iceq_isolation_forest_results_v1.csv")
MODEL_PATH = Path("models/iceq_isolation_forest_v1.joblib")

# 2. Load the existing dataset
df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)

# 3. Select sensor features only
# Exclude timestamp, identifiers, and the future target.
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

X = df[features].copy()

# 4. Build the anomaly-detection pipeline
# StandardScaler puts features on comparable scales.
# Isolation Forest identifies unusual combinations of readings.
model = Pipeline([
    ("scaler", StandardScaler()),
    (
        "isolation_forest",
        IsolationForest(
            n_estimators=200,
            contamination="auto",
            random_state=42,
        ),
    ),
])

# 5. Fit the model on sensor readings
model.fit(X)

# 6. Calculate anomaly scores and labels
# Lower decision scores indicate more unusual observations.
anomaly_model = model.named_steps["isolation_forest"]
X_scaled = model.named_steps["scaler"].transform(X)

df["anomaly_score"] = anomaly_model.decision_function(X_scaled)
df["anomaly_label"] = anomaly_model.predict(X_scaled)

# -1 = unusual; 1 = not flagged as unusual
df["is_anomaly"] = df["anomaly_label"] == -1

# 7. Save results without modifying the source dataset
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

# 8. Save the trained model
import joblib

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(
    {"model": model, "features": features},
    MODEL_PATH,
)

# 9. Display a summary
print("\nIsolation Forest training completed.")
print("Rows analysed:", len(df))
print("Anomalies flagged:", int(df["is_anomaly"].sum()))
print(
    "Anomaly percentage:",
    round(df["is_anomaly"].mean() * 100, 2),
    "%",
)
print("\nAnomaly labels:")
print(df["anomaly_label"].value_counts().to_string())

print("\nSaved results:", OUTPUT_PATH)
print("Saved model:", MODEL_PATH)

print("\nFirst 10 flagged readings:")
print(
    df.loc[
        df["is_anomaly"],
        [
            "timestamp",
            "unit_id",
            "food_type",
            "temperature_current",
            "temperature_threshold_c",
            "anomaly_score",
        ],
    ]
    .head(10)
    .to_string(index=False)
)
