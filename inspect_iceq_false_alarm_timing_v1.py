
import pandas as pd

PREDICTIONS_PATH = "data/iceq_test_predictions_v1.csv"

df = pd.read_csv(PREDICTIONS_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Use the same threshold defined for each food type.
# These are the thresholds used in the simulated dataset.
thresholds = {
    "Dairy": 5.0,
    "Produce": 8.0,
    "Frozen": -15.0,
}

df["threshold"] = df["food_type"].map(thresholds)

# Actual temperature-threshold exceedance at each reading
df["actual_breach"] = (
    df["temperature_current"] > df["threshold"]
)

# Only inspect false-positive model predictions
false_alarms = df[
    (df["actual_future_exceedance"] == 0)
    & (df["predicted_future_exceedance"] == 1)
].copy()

# Check the next 30 minutes using actual readings from the same unit.
# This is a diagnostic, not a new model evaluation.
future_breach = []

for _, row in false_alarms.iterrows():
    future_rows = df[
        (df["unit_id"] == row["unit_id"])
        & (df["timestamp"] > row["timestamp"])
        & (
            df["timestamp"]
            <= row["timestamp"] + pd.Timedelta(minutes=30)
        )
    ]

    future_breach.append(
        bool(future_rows["actual_breach"].any())
    )

false_alarms["breach_within_30m"] = future_breach

print("False-positive readings:", len(false_alarms))
print(
    "With an observed threshold breach in the following 30 minutes:",
    int(false_alarms["breach_within_30m"].sum()),
)
print(
    "Without an observed threshold breach in the following 30 minutes:",
    int((~false_alarms["breach_within_30m"]).sum()),
)

print("\nBy food type:")
print(
    false_alarms.groupby("food_type")["breach_within_30m"]
    .agg(["count", "sum", "mean"])
    .to_string()
)
