
from pathlib import Path

import pandas as pd

DATA = Path("data")
FILE = DATA / "iceq_model_error_comparison_v1.csv"

df = pd.read_csv(FILE)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Inspect false alarms from each model separately.
for model in ["catboost", "xgboost"]:
    predicted_col = f"{model}_predicted"

    false_alarms = df[
        (df["actual"] == 0) &
        (df[predicted_col] == 1)
    ].copy()

    print(f"\n{model.upper()} FALSE-ALARM SEQUENCES")
    print("=" * 50)

    for food_type, part in false_alarms.groupby("food_type"):
        part = part.sort_values("timestamp").copy()

        # Start a new sequence if the gap is greater than 5 minutes.
        part["new_sequence"] = (
            part["timestamp"].diff().dt.total_seconds().div(60).ne(5)
        )
        part["sequence_id"] = part["new_sequence"].cumsum()

        sequences = part.groupby("sequence_id").agg(
            start=("timestamp", "min"),
            end=("timestamp", "max"),
            readings=("timestamp", "size"),
            mean_temperature=("temperature_current", "mean"),
            mean_probability=(f"{model}_probability", "mean"),
        ).reset_index(drop=True)

        print(f"\n{food_type}: {len(sequences)} sequences")
        if not sequences.empty:
            print("Longest sequences:")
            print(
                sequences.sort_values("readings", ascending=False)
                .head(10)
                .round(3)
                .to_string(index=False)
            )
