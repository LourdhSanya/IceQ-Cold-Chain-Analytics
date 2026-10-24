
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

FILE = "data/iceq_anomaly_chronological_validation_v1.csv"

df = pd.read_csv(FILE)
target = "target_future_exceedance_30m"

# Lower decision_function scores mean more anomalous.
# Negate the score so higher values mean more anomalous.
df["anomaly_strength"] = -df["anomaly_score"]

print("\nICEQ ANOMALY SCORE RANKING")
print("=" * 45)

for food_type, part in df.groupby("food_type"):
    y = part[target].astype(int)
    scores = part["anomaly_strength"]

    print(f"\nFood type: {food_type}")
    print("Readings:", len(part))
    print("Positive readings:", int(y.sum()))

    if y.nunique() < 2:
        print("Ranking metrics unavailable: only one target class.")
        continue

    print(f"Average precision: {average_precision_score(y, scores):.4f}")
    print(f"ROC-AUC: {roc_auc_score(y, scores):.4f}")

    print("\nMean anomaly strength:")
    print("Positive readings:", round(scores[y == 1].mean(), 4))
    print("Negative readings:", round(scores[y == 0].mean(), 4))

# Overall ranking
y = df[target].astype(int)
scores = df["anomaly_strength"]

print("\nOVERALL")
if y.nunique() == 2:
    print(f"Average precision: {average_precision_score(y, scores):.4f}")
    print(f"ROC-AUC: {roc_auc_score(y, scores):.4f}")
else:
    print("Ranking metrics unavailable: only one target class.")
