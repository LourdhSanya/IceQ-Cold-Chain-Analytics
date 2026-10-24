
import pandas as pd
from pathlib import Path
from sklearn.metrics import confusion_matrix, classification_report

# Load anomaly results
results = pd.read_csv(
    "data/iceq_isolation_forest_results_v1.csv"
)

# Load the original simulated readings with incident labels
sensor_data = pd.read_csv(
    "data/iceq_simulated_readings_v2.csv"
)

# Match each reading using its timestamp and unit
results["timestamp"] = pd.to_datetime(results["timestamp"])
sensor_data["timestamp"] = pd.to_datetime(sensor_data["timestamp"])

comparison = results.merge(
    sensor_data[
        ["timestamp", "unit_id", "incident_active", "threshold_exceeded"]
    ],
    on=["timestamp", "unit_id"],
    how="left",
    validate="one_to_one",
)

# Convert incident labels into True/False
comparison["actual_incident"] = (
    comparison["incident_active"].astype(int) == 1
)

comparison["predicted_anomaly"] = comparison["is_anomaly"].astype(bool)

# Compare anomaly flags with incident readings
tn, fp, fn, tp = confusion_matrix(
    comparison["actual_incident"],
    comparison["predicted_anomaly"],
    labels=[False, True],
).ravel()

print("=== Isolation Forest vs. Incident Labels ===")
print("Total matched readings:", len(comparison))
print("Actual incident readings:", int(comparison["actual_incident"].sum()))
print("Anomalies flagged:", int(comparison["predicted_anomaly"].sum()))

print("\nConfusion matrix counts:")
print("True negatives (TN):", tn)
print("False positives (FP):", fp)
print("False negatives (FN):", fn)
print("True positives (TP):", tp)

recall = tp / (tp + fn) if (tp + fn) else 0
precision = tp / (tp + fp) if (tp + fp) else 0

print("\nIncident recall:", round(recall, 4))
print("Incident precision:", round(precision, 4))

print("\nAnomaly flags by unit:")
print(
    comparison.groupby("unit_id")["predicted_anomaly"]
    .agg(["sum", "count", "mean"])
    .to_string()
)

print("\nIncident readings flagged by anomaly detection:")
print(
    comparison.loc[
        comparison["actual_incident"] & comparison["predicted_anomaly"],
        [
            "timestamp",
            "unit_id",
            "temperature_current",
            "temperature_threshold_c",
            "anomaly_score",
        ],
    ]
    .head(15)
    .to_string(index=False)
)

output_path = Path("data/iceq_anomaly_evaluation_v1.csv")
comparison.to_csv(output_path, index=False)

print("\nSaved comparison:", output_path)
