
import pandas as pd
from pathlib import Path
from sklearn.metrics import confusion_matrix

from catboost import CatBoostClassifier
from xgboost import XGBClassifier

DATA_DIR = Path("data")
MODEL_DIR = Path("models")

TARGET = "target_future_exceedance_30m"

FEATURES = [
    "unit_id",
    "food_type",
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
    "hour",
    "day_of_week",
]

# Load the same validation dataset used by both models.
valid = pd.read_csv(DATA_DIR / "iceq_validation_v1.csv")

cat_predictions = pd.read_csv(
    DATA_DIR / "iceq_validation_predictions_v1.csv"
)

xgb_predictions = pd.read_csv(
    DATA_DIR / "iceq_xgboost_validation_predictions_v1.csv"
)

# Ensure predictions match the validation rows.
assert len(valid) == len(cat_predictions) == len(xgb_predictions), (
    "Row counts do not match. Stop and investigate before comparing."
)

assert (
    valid[TARGET].astype(int).to_list()
    == cat_predictions[TARGET].astype(int).to_list()
    == xgb_predictions[TARGET].astype(int).to_list()
), "Target labels do not match. Stop and investigate."

report = valid.copy()
report["catboost_probability"] = (
    cat_predictions["predicted_probability"].to_numpy()
)
report["xgboost_probability"] = (
    xgb_predictions["predicted_probability"].to_numpy()
)

# Compare both models at the existing threshold of 0.50.
actual = report[TARGET].astype(int)

for model_name in ["catboost", "xgboost"]:
    probability = report[f"{model_name}_probability"]
    predicted = (probability >= 0.50).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        actual, predicted, labels=[0, 1]
    ).ravel()

    print(f"\n{'=' * 45}")
    print(model_name.upper(), "ERROR ANALYSIS")
    print("=" * 45)
    print("True positives:", tp)
    print("False alarms:", fp)
    print("True negatives:", tn)
    print("Missed positive cases:", fn)

# Inspect false alarms from each model.
# These are cases predicted positive but labelled negative.
for model_name in ["catboost", "xgboost"]:
    probability = report[f"{model_name}_probability"]

    false_alarms = report[
        (probability >= 0.50) & (actual == 0)
    ].copy()

    print(f"\n{model_name.upper()} - FALSE ALARM EXAMPLES")
    print("Number of false alarms:", len(false_alarms))

    columns = [
        "timestamp",
        "unit_id",
        "food_type",
        "temperature_current",
        "temperature_threshold_c",
        "temperature_margin",
        "temperature_change_5m",
        "temperature_change_15m",
        "temperature_change_30m",
        "humidity_current",
        f"{model_name}_probability",
    ]

    print(
        false_alarms[columns]
        .sort_values(f"{model_name}_probability", ascending=False)
        .head(10)
        .round(3)
        .to_string(index=False)
    )

# Load saved models to inspect feature importance.
cat_model = CatBoostClassifier()
cat_model.load_model(str(MODEL_DIR / "iceq_catboost_v1.cbm"))

xgb_model = XGBClassifier()
xgb_model.load_model(str(MODEL_DIR / "iceq_xgboost_v1.json"))

cat_importance = pd.Series(
    cat_model.get_feature_importance(),
    index=FEATURES,
    name="CatBoost",
)

xgb_importance = pd.Series(
    xgb_model.feature_importances_,
    index=FEATURES,
    name="XGBoost",
)

importance = pd.concat(
    [cat_importance, xgb_importance], axis=1
).fillna(0)

print("\n" + "=" * 45)
print("FEATURE IMPORTANCE")
print("=" * 45)
print(
    importance.sort_values("CatBoost", ascending=False)
    .round(4)
    .to_string()
)

# Save a report for later investigation.
report.to_csv(
    DATA_DIR / "iceq_model_diagnostics_v1.csv",
    index=False,
)

importance.to_csv(
    DATA_DIR / "iceq_feature_importance_v1.csv"
)

print("\nSaved:")
print("data/iceq_model_diagnostics_v1.csv")
print("data/iceq_feature_importance_v1.csv")
print("\nNo model was retrained. The test set was not used.")
