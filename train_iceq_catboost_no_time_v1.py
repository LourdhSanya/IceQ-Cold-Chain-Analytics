
import json
import numpy as np
import pandas as pd

from pathlib import Path
from catboost import CatBoostClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

# --------------------------------------------------
# 1. Paths and settings
# --------------------------------------------------
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
]

CATEGORICAL = ["unit_id", "food_type"]

# --------------------------------------------------
# 2. Load training and validation data
# --------------------------------------------------
train = pd.read_csv(DATA_DIR / "iceq_train_v1.csv")
valid = pd.read_csv(DATA_DIR / "iceq_validation_v1.csv")

X_train = train[FEATURES].copy()
y_train = train[TARGET].astype(int)

X_valid = valid[FEATURES].copy()
y_valid = valid[TARGET].astype(int)

print("=" * 60)
print("ICEQ CATBOOST TRAINING")
print("=" * 60)

print("Training rows:", len(train))
print("Validation rows:", len(valid))
print("Training positive cases:", int(y_train.sum()))
print("Validation positive cases:", int(y_valid.sum()))

# --------------------------------------------------
# 3. Baseline: always predict the majority class
# --------------------------------------------------
baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(X_train, y_train)

baseline_predictions = baseline.predict(X_valid)

print("\nBASELINE VALIDATION RESULTS")
print("Precision:",
      round(precision_score(y_valid, baseline_predictions,
                            zero_division=0), 4))
print("Recall:",
      round(recall_score(y_valid, baseline_predictions,
                         zero_division=0), 4))
print("F1:",
      round(f1_score(y_valid, baseline_predictions,
                     zero_division=0), 4))

# --------------------------------------------------
# 4. Train CatBoost
# --------------------------------------------------
model = CatBoostClassifier(
    iterations=500,
    depth=6,
    learning_rate=0.03,
    loss_function="Logloss",
    eval_metric="PRAUC",
    auto_class_weights="Balanced",
    random_seed=42,
    verbose=100,
    allow_writing_files=False,
)

model.fit(
    X_train,
    y_train,
    cat_features=CATEGORICAL,
    eval_set=(X_valid, y_valid),
    early_stopping_rounds=75,
    verbose=100,
)

# --------------------------------------------------
# 5. Evaluate on validation data
# --------------------------------------------------
probabilities = model.predict_proba(X_valid)[:, 1]
predictions = (probabilities >= 0.5).astype(int)

print("\nCATBOOST VALIDATION RESULTS")
print("Average precision (PR-AUC summary):",
      round(average_precision_score(y_valid, probabilities), 4))
print("Precision at threshold 0.50:",
      round(precision_score(y_valid, predictions,
                            zero_division=0), 4))
print("Recall at threshold 0.50:",
      round(recall_score(y_valid, predictions,
                         zero_division=0), 4))
print("F1 at threshold 0.50:",
      round(f1_score(y_valid, predictions,
                     zero_division=0), 4))

tn, fp, fn, tp = confusion_matrix(
    y_valid, predictions, labels=[0, 1]
).ravel()

print("\nConfusion matrix counts at threshold 0.50")
print("True negatives:", tn)
print("False positives:", fp)
print("False negatives:", fn)
print("True positives:", tp)

# --------------------------------------------------
# 6. Save model and metadata
# --------------------------------------------------
model_path = MODEL_DIR / "iceq_catboost_no_time_v1.cbm"
model.save_model(str(model_path))

metadata = {
    "target": TARGET,
    "prediction_horizon_minutes": 30,
    "features": FEATURES,
    "categorical_features": CATEGORICAL,
    "validation_threshold": 0.5,
    "test_set_used": False,
    "data_source": "simulated",
}

metadata_path = MODEL_DIR / "iceq_catboost_no_time_v1_metadata.json"
metadata_path.write_text(json.dumps(metadata, indent=2))

# Save validation probabilities for later threshold analysis.
validation_output = valid[["timestamp", TARGET]].copy()
validation_output["predicted_probability"] = probabilities
validation_output.to_csv(
    DATA_DIR / "iceq_validation_predictions_no_time_v1.csv",
    index=False,
)

print("\nSaved model:", model_path.resolve())
print("Saved metadata:", metadata_path.resolve())
print("Saved validation predictions:",
      (DATA_DIR / "iceq_validation_predictions_no_time_v1.csv").resolve())
print("\nTraining complete. The test dataset was not used.")
