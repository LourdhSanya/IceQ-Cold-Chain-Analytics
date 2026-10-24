
import pandas as pd

df = pd.read_csv("data/iceq_anomaly_evaluation_v1.csv")

df["threshold_margin"] = (
    df["temperature_current"] - df["temperature_threshold_c"]
)

print("=== Anomaly Summary by Unit ===")

summary = df.groupby("unit_id").agg(
    total_readings=("is_anomaly", "size"),
    anomalies=("is_anomaly", "sum"),
    incident_readings=("actual_incident", "sum"),
    threshold_exceedances=("threshold_exceeded", "sum"),
)

summary["anomaly_pct"] = (
    summary["anomalies"] / summary["total_readings"] * 100
).round(2)

print(summary.to_string())

print("\n=== Flagged Anomalies by Food Type ===")

flagged = df[df["is_anomaly"]].copy()

print(
    flagged.groupby("food_type").agg(
        anomalies=("is_anomaly", "size"),
        mean_temperature=("temperature_current", "mean"),
        min_temperature=("temperature_current", "min"),
        max_temperature=("temperature_current", "max"),
        mean_threshold_margin=("threshold_margin", "mean"),
        incident_readings=("actual_incident", "sum"),
    ).round(2).to_string()
)

print("\n=== Most Unusual Readings ===")

print(
    df.nsmallest(15, "anomaly_score")[
        [
            "timestamp",
            "unit_id",
            "food_type",
            "temperature_current",
            "temperature_threshold_c",
            "threshold_margin",
            "actual_incident",
            "anomaly_score",
        ]
    ].to_string(index=False)
)
