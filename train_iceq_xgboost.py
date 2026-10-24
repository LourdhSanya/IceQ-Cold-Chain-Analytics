
import pandas as pd
from pathlib import Path

from xgboost import XGBClassifier
from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

DATA_DIR = Path("data")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

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

# Load the same chronological split used for CatBoost.
train = pd.read_csv(DATA_DIR / "iceq_train_v1.csv")
valid = pd.read_csv(DATA_DIR / "iceq_validation_v1.csv")

X_train = train[FEATURES].copy()
X_valid = valid[FEATURES].copy()
y_train = train[TARGET].astype(int)
y_valid = valid[TARGET].astype(int)

# XGBoost needs categorical values encoded as category codes.
for column in ["unit_id", "food_type"]:
    combined = pd.concat(
        [X_train[column], X_valid[column]],
        ignore_index=True
    ).astype("category")

    categories = combined.cat.categories

    X_train[column] = pd.Categorical(
        X_train[column], categories=categories
    ).codes

    X_valid[column] = pd.Categorical(
        X_valid[column], categories=categories
    ).codes

# Give more weight to positive training examples.
positive_count = int(y_train.sum())
negative_count = len(y_train) - positive_count
class_weight = negative_count / positive_count

model = XGBClassifier(
    n_estimators=500,
    max_depth=4,
    learning_rate=0.03,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="binary:logistic",
    eval_metric="aucpr",
    scale_pos_weight=class_weight,
    random_state=42,
    early_stopping_rounds=75,
    n_jobs=-1,
)

model.fit(
    X_train,
    y_train,
    eval_set=[(X_valid, y_valid)],
    verbose=False,
)

# Evaluate on validation only, at the same 0.50 threshold.
probabilities = model.predict_proba(X_valid)[:, 1]
predictions = (probabilities >= 0.50).astype(int)

print("=" * 55)
print("ICEQ XGBOOST VALIDATION RESULTS")
print("=" * 55)

print("Best iteration:", model.best_iteration)
print(
    "Average precision:",
    round(average_precision_score(y_valid, probabilities), 4)
)
print(
    "Precision:",
    round(precision_score(y_valid, predictions, zero_division=0), 4)
)
print(
    "Recall:",
    round(recall_score(y_valid, predictions, zero_division=0), 4)
)
print(
    "F1-score:",
    round(f1_score(y_valid, predictions, zero_division=0), 4)
)

tn, fp, fn, tp = confusion_matrix(
    y_valid, predictions, labels=[0, 1]
).ravel()

print("\nTrue positives:", tp)
print("False positives:", fp)
print("True negatives:", tn)
print("False negatives:", fn)

model.save_model(str(MODEL_DIR / "iceq_xgboost_v1.json"))

output = valid[["timestamp", TARGET]].copy()
output["predicted_probability"] = probabilities
output.to_csv(
    DATA_DIR / "iceq_xgboost_validation_predictions_v1.csv",
    index=False,
)

print("\nSaved model: models/iceq_xgboost_v1.json")
print("Saved validation predictions.")
print("The final test set was not used.")
