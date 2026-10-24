
from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import confusion_matrix, precision_score, recall_score

# 1. File locations
TRAIN_FILE = Path("data/iceq_train_v1.csv")
VALIDATION_FILE = Path("data/iceq_validation_v1.csv")
OUTPUT_FILE = Path("data/iceq_anomaly_chronological_validation_v1.csv")

# 2. Load only training and validation data
train_df = pd.read_csv(TRAIN_FILE)
validation_df = pd.read_csv(VALIDATION_FILE)

TARGET = "target_future_exceedance_30m"

FEATURES = [
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

# 3. Check that the required columns exist
for column in FEATURES + [TARGET, "food_type"]:
    if column not in train_df.columns or column not in validation_df.columns:
        raise ValueError(f"Required column missing: {column}")

# 4. Train a separate model for each food type
results = []
summary = []

for food_type in sorted(train_df["food_type"].unique()):

    train_part = train_df[train_df["food_type"] == food_type].copy()
    validation_part = validation_df[
        validation_df["food_type"] == food_type
    ].copy()

    if validation_part.empty:
        continue

    # Fit on historical training readings only.
    # Do not use the future target as an input feature.
    model = IsolationForest(
        n_estimators=200,
        contamination="auto",
        random_state=42,
    )

    model.fit(train_part[FEATURES])

    # Predict anomalies on later validation readings
    predictions = model.predict(validation_part[FEATURES])

    validation_part["anomaly_flag"] = (predictions == -1).astype(int)
    validation_part["food_type_model"] = food_type

    # Lower decision scores indicate more abnormal observations.
    validation_part["anomaly_score"] = model.decision_function(
        validation_part[FEATURES]
    )

    results.append(validation_part)

# 5. Combine validation predictions
if not results:
    raise ValueError("No validation predictions were generated.")

output_df = pd.concat(results, ignore_index=True)
output_df.to_csv(OUTPUT_FILE, index=False)

# 6. Evaluate against the simulated future-exceedance target
print("\nICEQ CHRONOLOGICAL ISOLATION FOREST EVALUATION")
print("=" * 55)
print("Training data:", TRAIN_FILE)
print("Validation data:", VALIDATION_FILE)
print("Test data: NOT USED")

for food_type in sorted(output_df["food_type"].unique()):

    part = output_df[output_df["food_type"] == food_type]

    actual = part[TARGET].astype(int)
    predicted = part["anomaly_flag"].astype(int)

    tn, fp, fn, tp = confusion_matrix(
        actual, predicted, labels=[0, 1]
    ).ravel()

    precision = precision_score(
        actual, predicted, zero_division=0
    )
    recall = recall_score(
        actual, predicted, zero_division=0
    )

    print(f"\nFood type: {food_type}")
    print("Validation readings:", len(part))
    print("Actual future-exceedance positives:", int(actual.sum()))
    print("Anomaly alerts:", int(predicted.sum()))
    print("True positives:", tp)
    print("False positives:", fp)
    print("Missed positives:", fn)
    print("True negatives:", tn)
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")

# 7. Overall results
actual = output_df[TARGET].astype(int)
predicted = output_df["anomaly_flag"].astype(int)

tn, fp, fn, tp = confusion_matrix(
    actual, predicted, labels=[0, 1]
).ravel()

print("\nOVERALL VALIDATION RESULTS")
print("-" * 35)
print("Readings:", len(output_df))
print("Actual positives:", int(actual.sum()))
print("Anomaly alerts:", int(predicted.sum()))
print("True positives:", tp)
print("False positives:", fp)
print("Missed positives:", fn)
print("True negatives:", tn)
print(f"Precision: {precision_score(actual, predicted, zero_division=0):.4f}")
print(f"Recall: {recall_score(actual, predicted, zero_division=0):.4f}")

print("\nSaved validation predictions to:", OUTPUT_FILE)
