
import json
import pandas as pd

from catboost import CatBoostClassifier
from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

# 1. File paths
TEST_PATH = "data/iceq_test_v1.csv"
MODEL_PATH = "models/iceq_catboost_v1.cbm"
METADATA_PATH = "models/iceq_catboost_v1_metadata.json"
OUTPUT_PATH = "data/iceq_test_predictions_v1.csv"

# 2. Load model configuration
with open(METADATA_PATH, "r") as file:
    metadata = json.load(file)

features = metadata["features"]
target = metadata["target"]
threshold = metadata["validation_threshold"]

# 3. Load untouched test data
test_df = pd.read_csv(TEST_PATH)

X_test = test_df[features]
y_test = test_df[target].astype(int)

# 4. Load the trained model
model = CatBoostClassifier()
model.load_model(MODEL_PATH)

# 5. Predict probabilities
probabilities = model.predict_proba(X_test)[:, 1]

# Keep the threshold fixed at 0.50
predictions = (probabilities >= threshold).astype(int)

# 6. Evaluate results
tn, fp, fn, tp = confusion_matrix(
    y_test, predictions, labels=[0, 1]
).ravel()

print("\n===== ICEQ CATBOOST TEST EVALUATION =====")
print("Data source:", metadata["data_source"])
print("Prediction horizon:", metadata["prediction_horizon_minutes"], "minutes")
print("Test rows:", len(test_df))
print("Actual positive readings:", int(y_test.sum()))
print("Threshold:", threshold)

print("\n--- Confusion Matrix Counts ---")
print("True Positives (TP):", tp)
print("False Positives (FP):", fp)
print("False Negatives (FN):", fn)
print("True Negatives (TN):", tn)

print("\n--- Evaluation Metrics ---")
print(f"Precision: {precision_score(y_test, predictions, zero_division=0):.4f}")
print(f"Recall:    {recall_score(y_test, predictions, zero_division=0):.4f}")
print(f"F1 Score:  {f1_score(y_test, predictions, zero_division=0):.4f}")
print(f"Average Precision: {average_precision_score(y_test, probabilities):.4f}")

# 7. Results by food type
print("\n--- Results by Food Type ---")

for food_type, group in test_df.groupby("food_type"):
    indices = group.index
    actual = y_test.loc[indices]
    predicted = pd.Series(predictions, index=test_df.index).loc[indices]

    group_tp = int(((actual == 1) & (predicted == 1)).sum())
    group_fp = int(((actual == 0) & (predicted == 1)).sum())
    group_fn = int(((actual == 1) & (predicted == 0)).sum())
    group_tn = int(((actual == 0) & (predicted == 0)).sum())

    print(f"\n{food_type}")
    print("Rows:", len(group))
    print("Actual positive readings:", int(actual.sum()))
    print(f"TP={group_tp}, FP={group_fp}, FN={group_fn}, TN={group_tn}")

# 8. Save individual predictions
results = test_df.copy()
results["actual_future_exceedance"] = y_test
results["predicted_probability"] = probabilities
results["predicted_future_exceedance"] = predictions
results.to_csv(OUTPUT_PATH, index=False)

print("\nPredictions saved to:", OUTPUT_PATH)
print("Test evaluation completed.")
