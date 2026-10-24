
from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

DATA = Path("data")
TARGET = "target_future_exceedance_30m"
THRESHOLD = 0.50

# Load files
valid = pd.read_csv(DATA / "iceq_validation_v1.csv")
cat = pd.read_csv(DATA / "iceq_validation_predictions_v1.csv")
xgb = pd.read_csv(DATA / "iceq_xgboost_validation_predictions_v1.csv")

# Verify prediction files match the original validation rows.
if not (len(valid) == len(cat) == len(xgb)):
    raise ValueError("Row counts differ. Cannot safely compare predictions.")

for name, predictions in [("CatBoost", cat), ("XGBoost", xgb)]:
    if not valid["timestamp"].astype(str).reset_index(drop=True).equals(
        predictions["timestamp"].astype(str).reset_index(drop=True)
    ):
        raise ValueError(f"{name}: timestamp order differs from validation data.")

    if not valid[TARGET].reset_index(drop=True).equals(
        predictions[TARGET].reset_index(drop=True)
    ):
        raise ValueError(f"{name}: target order differs from validation data.")

# Safe to align by row position because both scripts predict valid in its original order.
comparison = valid[
    ["timestamp", "unit_id", "food_type", "temperature_current",
     "temperature_threshold_c", "temperature_margin", TARGET]
].copy()

comparison["catboost_probability"] = cat["predicted_probability"].to_numpy()
comparison["xgboost_probability"] = xgb["predicted_probability"].to_numpy()

comparison["actual"] = comparison[TARGET].astype(int)

for model in ["catboost", "xgboost"]:
    comparison[f"{model}_predicted"] = (
        comparison[f"{model}_probability"] >= THRESHOLD
    ).astype(int)

# Overall comparison
print("\nICEQ VALIDATION MODEL COMPARISON")
print("=" * 55)
print("Rows:", len(comparison))
print("Actual positives:", int(comparison["actual"].sum()))
print("Probability threshold:", THRESHOLD)
print("Test set used: NO")

for model in ["catboost", "xgboost"]:
    actual = comparison["actual"]
    predicted = comparison[f"{model}_predicted"]
    probability = comparison[f"{model}_probability"]

    tn, fp, fn, tp = confusion_matrix(
        actual, predicted, labels=[0, 1]
    ).ravel()

    print(f"\n{model.upper()}")
    print(f"TP={tp}, FP={fp}, FN={fn}, TN={tn}")
    print(f"Precision: {precision_score(actual, predicted, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(actual, predicted, zero_division=0):.4f}")
    print(f"F1:        {f1_score(actual, predicted, zero_division=0):.4f}")
    print(f"Average precision: {average_precision_score(actual, probability):.4f}")

# Per-food-type comparison
print("\nBY FOOD TYPE")
print("=" * 55)

for food_type, part in comparison.groupby("food_type"):
    print(f"\n{food_type}: rows={len(part)}, positives={int(part['actual'].sum())}")

    for model in ["catboost", "xgboost"]:
        actual = part["actual"]
        predicted = part[f"{model}_predicted"]

        tn, fp, fn, tp = confusion_matrix(
            actual, predicted, labels=[0, 1]
        ).ravel()

        print(f"{model.upper()}: TP={tp}, FP={fp}, FN={fn}, TN={tn}")

# Find errors and cases where models disagree
for model in ["catboost", "xgboost"]:
    comparison[f"{model}_error"] = (
        comparison["actual"] != comparison[f"{model}_predicted"]
    )

errors = comparison[
    comparison["catboost_error"] | comparison["xgboost_error"]
].copy()

def classify_error(row):
    if row["actual"] == 1:
        if row["catboost_predicted"] == 0 and row["xgboost_predicted"] == 0:
            return "Both missed positive"
        if row["catboost_predicted"] == 0:
            return "CatBoost missed positive"
        if row["xgboost_predicted"] == 0:
            return "XGBoost missed positive"
    else:
        if row["catboost_predicted"] == 1 and row["xgboost_predicted"] == 1:
            return "Both false alarm"
        if row["catboost_predicted"] == 1:
            return "CatBoost false alarm"
        if row["xgboost_predicted"] == 1:
            return "XGBoost false alarm"
    return "Check"

errors["error_type"] = errors.apply(classify_error, axis=1)

output = DATA / "iceq_model_error_comparison_v1.csv"
errors.to_csv(output, index=False)

print("\nERROR CATEGORIES")
print("=" * 55)
print(errors["error_type"].value_counts().to_string())
print("\nSaved error details:", output)

# Show a sample of errors with operational context
print("\nSAMPLE ERROR READINGS")
print("=" * 55)
columns = [
    "timestamp", "unit_id", "food_type", "temperature_current",
    "temperature_threshold_c", "actual",
    "catboost_probability", "catboost_predicted",
    "xgboost_probability", "xgboost_predicted", "error_type",
]
print(errors[columns].head(20).to_string(index=False))
