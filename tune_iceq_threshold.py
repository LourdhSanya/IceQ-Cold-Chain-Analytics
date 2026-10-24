
import pandas as pd

from pathlib import Path
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

# Load saved validation predictions
path = Path("data/iceq_validation_predictions_v1.csv")
df = pd.read_csv(path)

target = "target_future_exceedance_30m"
y_true = df[target].astype(int)
probabilities = df["predicted_probability"]

print("=" * 75)
print("ICEQ VALIDATION THRESHOLD COMPARISON")
print("=" * 75)

print(
    f"{'Threshold':>10} {'Precision':>10} {'Recall':>10} "
    f"{'F1':>10} {'TP':>6} {'FP':>6} {'FN':>6}"
)

results = []

for threshold in [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]:
    predictions = (probabilities >= threshold).astype(int)

    precision = precision_score(
        y_true, predictions, zero_division=0
    )
    recall = recall_score(
        y_true, predictions, zero_division=0
    )
    f1 = f1_score(
        y_true, predictions, zero_division=0
    )

    tn, fp, fn, tp = confusion_matrix(
        y_true, predictions, labels=[0, 1]
    ).ravel()

    results.append({
        "threshold": threshold,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    })

    print(
        f"{threshold:>10.2f} {precision:>10.3f} "
        f"{recall:>10.3f} {f1:>10.3f} "
        f"{tp:>6} {fp:>6} {fn:>6}"
    )

# Save the complete comparison for reporting
output = Path("data/iceq_threshold_comparison_v1.csv")
pd.DataFrame(results).to_csv(output, index=False)

print("\nSaved comparison:", output.resolve())
print(
    "\nChoose a threshold based on the desired balance "
    "between catching events and limiting false alarms."
)
