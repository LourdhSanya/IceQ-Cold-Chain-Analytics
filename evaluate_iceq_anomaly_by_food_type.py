
import pandas as pd
from sklearn.metrics import confusion_matrix

# Load the results from the separate food-type models
df = pd.read_csv("data/iceq_anomaly_by_food_type_v1.csv")

# Load the original incident labels
sensor = pd.read_csv("data/iceq_simulated_readings_v2.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])
sensor["timestamp"] = pd.to_datetime(sensor["timestamp"])

# Match readings to their original labels
df = df.merge(
    sensor[["timestamp", "unit_id", "incident_active"]],
    on=["timestamp", "unit_id"],
    how="left",
    validate="one_to_one",
)

df["actual_incident"] = df["incident_active"].astype(int) == 1
df["predicted_anomaly"] = df["is_anomaly"].astype(bool)

print("=== Separate Isolation Forest Evaluation ===")

for food_type in sorted(df["food_type"].unique()):
    part = df[df["food_type"] == food_type]

    tn, fp, fn, tp = confusion_matrix(
        part["actual_incident"],
        part["predicted_anomaly"],
        labels=[False, True],
    ).ravel()

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0

    print(f"\n{food_type}")
    print("Readings:", len(part))
    print("Incident readings:", int(part["actual_incident"].sum()))
    print("Anomalies flagged:", int(part["predicted_anomaly"].sum()))
    print("True positives:", tp)
    print("False positives:", fp)
    print("False negatives:", fn)
    print("True negatives:", tn)
    print("Precision:", round(precision, 4))
    print("Recall:", round(recall, 4))

tn, fp, fn, tp = confusion_matrix(
    df["actual_incident"],
    df["predicted_anomaly"],
    labels=[False, True],
).ravel()

print("\n=== Overall Results ===")
print("True positives:", tp)
print("False positives:", fp)
print("False negatives:", fn)
print("True negatives:", tn)
print("Incident recall:", round(tp / (tp + fn), 4))
print("Incident precision:", round(tp / (tp + fp), 4))

print("\nNote: these are exploratory in-sample results.")
