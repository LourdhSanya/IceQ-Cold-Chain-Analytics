
from pathlib import Path

import pandas as pd

DATA = Path("data")

readings = pd.read_csv(
    DATA / "iceq_ml_dataset_clean_v1.csv",
    parse_dates=["timestamp"],
)

errors = pd.read_csv(
    DATA / "iceq_model_error_comparison_v1.csv",
    parse_dates=["timestamp"],
)

# Select readings incorrectly predicted positive by CatBoost.
false_alarms = errors[
    (errors["actual"] == 0) &
    (errors["catboost_predicted"] == 1)
].copy()

# Keep the complete original sensor history for Dairy.
dairy = readings[
    readings["food_type"] == "Dairy"
].copy()

dairy = dairy.sort_values("timestamp").reset_index(drop=True)

print("CATBOOST FALSE-ALARM FUTURE-TEMPERATURE CHECK")
print("=" * 55)

for _, alarm in false_alarms[
    false_alarms["food_type"] == "Dairy"
].head(10).iterrows():

    current_time = alarm["timestamp"]

    future = dairy[
        (dairy["timestamp"] > current_time) &
        (dairy["timestamp"] <= current_time + pd.Timedelta(hours=2))
    ].copy()

    threshold = alarm["temperature_threshold_c"]

    breached = future[
        future["temperature_current"] > threshold
    ]

    if breached.empty:
        result = "No breach in next 2 hours"
        first_breach = "None"
        minutes = "N/A"
    else:
        first_time = breached.iloc[0]["timestamp"]
        result = "Breach found within 2 hours"
        first_breach = str(first_time)
        minutes = int(
            (first_time - current_time).total_seconds() / 60
        )

    print(f"\nWarning time: {current_time}")
    print(f"Temperature: {alarm['temperature_current']:.2f} C")
    print(f"Model probability: {alarm['catboost_probability']:.3f}")
    print(f"Target in next 30 minutes: {alarm['actual']}")
    print(f"Future result: {result}")
    print(f"First breach time: {first_breach}")
    print(f"Minutes until breach: {minutes}")
